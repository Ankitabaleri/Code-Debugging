const esprima = require('esprima');

function divide(prog) {
    try {
        // Parse the JavaScript code into AST
        const ast = esprima.parseScript(prog, { range: true, comment: true, loc: true });
        let dividedBlocks = [];
        let progLines = prog.split("\n");
        
        // Helper function to extract code by line range
        function extractCodeByLines(startLine, endLine) {
            return progLines.slice(startLine - 1, endLine).join("\n");
        }
        
        // Process comments
        if (ast.comments && ast.comments.length > 0) {
            ast.comments.forEach((comment, index) => {
                let commentCode = extractCodeByLines(comment.loc.start.line, comment.loc.end.line);
                dividedBlocks.push({ 
                    id: index + 1, 
                    code: commentCode
                });
            });
        }
        
        // Start block ID after comments
        let blockId = ast.comments ? ast.comments.length + 1 : 1;
        
        // Function to determine if two statements should be combined
        function shouldCombine(stmt1, stmt2) {
            // Check if stmt1 is a variable declaration and stmt2 uses that variable
            if (stmt1.type === 'VariableDeclaration' && 
                stmt2.type === 'VariableDeclaration' || stmt2.type === 'ExpressionStatement') {
                
                // Get the variable names from stmt1
                const varNames = stmt1.declarations.map(d => d.id.name);
                
                // Check if any of these variables are used in stmt2
                const stmt2Code = extractCodeByLines(stmt2.loc.start.line, stmt2.loc.end.line);
                return varNames.some(name => 
                    stmt2Code.includes(name) && 
                    !stmt2Code.includes(`const ${name}`) && 
                    !stmt2Code.includes(`let ${name}`) && 
                    !stmt2Code.includes(`var ${name}`)
                );
            }
            return false;
        }
        
        // Process function declarations and their contents
        ast.body.forEach(node => {
            if (node.type === "FunctionDeclaration" && node.body && node.body.body) {
                const statements = node.body.body;
                
                // Keep track of statements to skip
                const skipIndices = new Set();
                
                for (let i = 0; i < statements.length; i++) {
                    // Skip if this statement should be skipped
                    if (skipIndices.has(i)) continue;
                    
                    const statement = statements[i];
                    
                    // Extract the statement code
                    let startLine = statement.loc.start.line;
                    let endLine = statement.loc.end.line;
                    
                    // Check if we should combine with the next statement
                    if (i < statements.length - 1 && 
                        shouldCombine(statement, statements[i+1])) {
                        // Combine with the next statement
                        endLine = statements[i+1].loc.end.line;
                        skipIndices.add(i+1);
                    }
                    
                    const code = extractCodeByLines(startLine, endLine);
                    
                    // Skip empty statements
                    if (code.trim() === '') continue;
                    
                    dividedBlocks.push({
                        id: blockId++,
                        code: code
                    });
                }
            }
        });
        
        // Ensure we have no empty blocks
        const finalBlocks = dividedBlocks
            .filter(block => block.code.trim() !== '')
            .map((block, index) => ({
                id: index + 1,
                code: block.code
            }));
            
        return [finalBlocks, null];
    } catch (e) {
        return [null, e.toString()];
    }
}

// Example JavaScript Code
const prog = `
function findCharLong(text) {
    // Write a function to find all words which are at least 4 characters long in a string by using regex.
    if (text === "") {
        return [];
    }
    const pat = /\\b\\w{4}\\b/;
    const res = text.match(pat);
    return res;
}
`;

const [dividedBlocks, error] = divide(prog);
if (error) {
    console.error("Error:", error);
} else {
    console.log("Divided Code Blocks:");
    dividedBlocks.forEach(block => {
        console.log(`Block ID: ${block.id}`);
        console.log("Block Code:");
        console.log(block.code);
        console.log("-".repeat(50));
    });
}