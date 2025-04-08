// const esprima = require('esprima');

// function divide(prog) {
//     try {
//         const ast = esprima.parseScript(prog, { range: true, comment: true, loc: true });
//         let dividedBlocks = [];
//         let progLines = prog.split("\n");
        
//         // Function to get the block of code based on line numbers
//         function extractBlockByLines(startLine, endLine) {
//             return progLines.slice(startLine - 1, endLine).join("\n");
//         }
        
//         // Add comment block with proper formatting
//         ast.comments.forEach((comment, index) => {
//             // Convert JavaScript comment to expected output format (triple quotes for docstring)
//             let commentText = comment.value.trim();
//             let formattedComment = `    """${commentText}"""`;
//             dividedBlocks.push({ id: index + 1, code: formattedComment });
//         });
        
//         // Start block ID after comments
//         let blockId = ast.comments.length + 1;
        
//         // Process function declarations and their contents
//         ast.body.forEach(node => {
//             if (node.type === "FunctionDeclaration") {
//                 // Skip the function declaration itself, we just want the internal blocks
                
//                 // Process function body statements
//                 if (node.body && node.body.body) {
//                     node.body.body.forEach(statement => {
//                         let code = "";
                        
//                         // Determine the line range for this statement
//                         const startLine = statement.loc.start.line;
//                         const endLine = statement.loc.end.line;
                        
//                         // Extract the code for this range
//                         code = extractBlockByLines(startLine, endLine);
                        
//                         // Transform JavaScript code to match expected Python-like output
//                         if (statement.type === "IfStatement") {
//                             // Convert JavaScript if to Python-like syntax
//                             code = code.replace(/if\s*\((.*)\)\s*{/, "    if $1:")
//                                      .replace(/{\s*/, "")
//                                      .replace(/}\s*/, "")
//                                      .replace(/===/, "==")
//                                      .replace(/return \[\];/, "        return []");
//                         } else if (statement.type === "VariableDeclaration") {
//                             // Convert JavaScript variable declarations to Python-like syntax
//                             if (code.includes("pat =")) {
//                                 code = code.replace(/const\s+pat\s*=\s*\/(.*)\/;/, "    pat = r\"\\$1\"");
//                             } else if (code.includes("res =")) {
//                                 // Convert to re.findall as in expected output
//                                 code = "    res = re.findall(pat, text)";
//                             }
//                         } else if (statement.type === "ReturnStatement") {
//                             // Just ensure proper indentation
//                             code = "    " + code.trim();
//                         }
                        
//                         dividedBlocks.push({ id: blockId++, code: code });
//                     });
//                 }
//             }
//         });
        
//         // Filter out any empty blocks
//         dividedBlocks = dividedBlocks.filter(block => block.code.trim() !== '');
        
//         // Ensure proper IDs
//         dividedBlocks.forEach((block, index) => {
//             block.id = index + 1;
//         });
        
//         return [dividedBlocks, null];
//     } catch (e) {
//         return [null, e.toString()];
//     }
// }

// // Example JavaScript Code
// const prog = `
// function findCharLong(text) {
//     // Write a function to find all words which are at least 4 characters long in a string by using regex.
//     if (text === "") {
//         return [];
//     }
//     const pat = /\\b\\w{4}\\b/;
//     const res = text.match(pat);
//     return res;
// }
// `;

// const [dividedBlocks, error] = divide(prog);
// if (error) {
//     console.error("Error:", error);
// } else {
//     console.log("Divided Code Blocks:");
//     dividedBlocks.forEach(block => {
//         console.log(`Block ID: ${block.id}`);
//         console.log("Block Code:");
//         console.log(block.code);
//         console.log("-".repeat(50));
//     });
// }

// const esprima = require('esprima');

// function divide(prog) {
//     try {
//         // Parse the JavaScript code into AST
//         const ast = esprima.parseScript(prog, { range: true, comment: true, loc: true });
//         let dividedBlocks = [];
//         let progLines = prog.split("\n");
        
//         // Helper function to extract code by range
//         function extractCodeBlock(node) {
//             const startLine = node.loc.start.line;
//             const endLine = node.loc.end.line;
//             return progLines.slice(startLine - 1, endLine).join("\n");
//         }
        
//         // Process comments first
//         if (ast.comments && ast.comments.length > 0) {
//             ast.comments.forEach((comment, index) => {
//                 let commentCode = extractCodeBlock(comment);
//                 dividedBlocks.push({ 
//                     id: index + 1, 
//                     code: commentCode,
//                     startLine: comment.loc.start.line,
//                     endLine: comment.loc.end.line
//                 });
//             });
//         }
        
//         // Start block ID after comments
//         let blockId = ast.comments ? ast.comments.length + 1 : 1;
        
//         // Process function bodies
//         const processNode = (node) => {
//             if (!node) return;
            
//             // Process different types of nodes
//             if (node.type === 'BlockStatement' && node.body) {
//                 // Process each statement in the block separately
//                 node.body.forEach(statement => {
//                     const code = extractCodeBlock(statement);
//                     dividedBlocks.push({
//                         id: blockId++,
//                         code: code,
//                         startLine: statement.loc.start.line,
//                         endLine: statement.loc.end.line
//                     });
                    
//                     // Recursively process nested blocks
//                     if (statement.consequent && statement.consequent.type === 'BlockStatement') {
//                         processNode(statement.consequent);
//                     }
//                     if (statement.alternate && statement.alternate.type === 'BlockStatement') {
//                         processNode(statement.alternate);
//                     }
//                 });
//             } else if (node.type === 'IfStatement') {
//                 // Process the test part and each branch of the if statement
//                 const code = extractCodeBlock(node);
//                 dividedBlocks.push({
//                     id: blockId++,
//                     code: code,
//                     startLine: node.loc.start.line,
//                     endLine: node.loc.end.line
//                 });
                
//                 // Process consequent and alternate blocks
//                 if (node.consequent) {
//                     processNode(node.consequent);
//                 }
//                 if (node.alternate) {
//                     processNode(node.alternate);
//                 }
//             } else if (node.body && Array.isArray(node.body)) {
//                 // For nodes with body arrays (like function declarations)
//                 node.body.forEach(childNode => {
//                     processNode(childNode);
//                 });
//             }
//         };
        
//         // Find top-level nodes
//         ast.body.forEach(node => {
//             if (node.type === 'FunctionDeclaration') {
//                 // Extract the function body for processing
//                 if (node.body && node.body.type === 'BlockStatement') {
//                     processNode(node.body);
//                 }
//             } else {
//                 // Process other top-level statements
//                 const code = extractCodeBlock(node);
//                 dividedBlocks.push({
//                     id: blockId++,
//                     code: code,
//                     startLine: node.loc.start.line,
//                     endLine: node.loc.end.line
//                 });
//             }
//         });
        
//         // Remove duplicates by comparing code content
//         const uniqueBlocks = [];
//         const seenCode = new Set();
        
//         dividedBlocks.forEach(block => {
//             const trimmedCode = block.code.trim();
//             if (trimmedCode && !seenCode.has(trimmedCode)) {
//                 seenCode.add(trimmedCode);
//                 uniqueBlocks.push({
//                     id: uniqueBlocks.length + 1,
//                     code: block.code
//                 });
//             }
//         });
        
//         return [uniqueBlocks, null];
//     } catch (e) {
//         return [null, e.toString()];
//     }
// }

// // Example JavaScript Code
// const prog = `
// function findCharLong(text) {
//     // Write a function to find all words which are at least 4 characters long in a string by using regex.
//     if (text === "") {
//         return [];
//     }
//     const pat = /\\b\\w{4}\\b/;
//     const res = text.match(pat);
//     return res;
// }
// `;

// const [dividedBlocks, error] = divide(prog);
// if (error) {
//     console.error("Error:", error);
// } else {
//     console.log("Divided Code Blocks:");
//     dividedBlocks.forEach(block => {
//         console.log(`Block ID: ${block.id}`);
//         console.log("Block Code:");
//         console.log(block.code);
//         console.log("-".repeat(50));
//     });
// }

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