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

function divideHeuristically(prog) {
    const lines = prog.split("\n");
    const blocks = [];
    let currentBlock = [];
    let id = 1;
    let braceDepth = 0;

    const commentBuffer = [];
    let foundFirstStatement = false;

    const flushBlock = () => {
        if (currentBlock.length > 0) {
            blocks.push({ id: id++, code: currentBlock.join("\n") });
            currentBlock = [];
        }
    };

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Buffer top comments
        if (!foundFirstStatement && (trimmed === '' || trimmed.startsWith('//'))) {
            commentBuffer.push(line);
            continue;
        }

        // First real code: prepend comment buffer
        if (!foundFirstStatement) {
            if (commentBuffer.length > 0) {
                currentBlock.push(...commentBuffer);
                commentBuffer.length = 0;
            }
            foundFirstStatement = true;
        }

        currentBlock.push(line);

        // Update brace depth
        for (const char of trimmed) {
            if (char === '{') braceDepth++;
            if (char === '}') braceDepth--;
        }

        const endsWithSemicolon = trimmed.endsWith(';');
        const isStandaloneBrace = trimmed === '{' || trimmed === '}';
        const isControlFlow = /^(if|for|while|switch|else)\b/.test(trimmed);
        const isReturn = trimmed.startsWith('return');
        const isBreak = trimmed.startsWith('break');
        const isContinue = trimmed.startsWith('continue');
        const isThrow = trimmed.startsWith('throw');

        const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : "";

        const shouldFlush =
            (braceDepth === 0 && endsWithSemicolon) ||
            isStandaloneBrace ||
            isReturn || isBreak || isContinue || isThrow ||
            (!isControlFlow && braceDepth === 0 && nextLine === "");

        if (shouldFlush) {
            flushBlock();
        }
    }

    flushBlock();

    return blocks;
}

const fs = require('fs');
let input = '';

process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    const [blocks, error] = divide(input);
    if (error) {
        // fallback to heuristic if needed
        const fallbackBlocks = divideHeuristically(input);
        console.log(JSON.stringify(fallbackBlocks));
    } else {
        console.log(JSON.stringify(blocks));
    }
});