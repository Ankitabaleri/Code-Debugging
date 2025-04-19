// divide_heuristic.js -- This is to divide only incorrect blocks i.e. buggy code
const readline = require("readline");
let input = '';
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => input += chunk);
process.stdin.on("end", () => {
    const lines = input.split("\n");
    const blocks = [];
    let currentBlock = [];
    let blockId = 1;
    let braceDepth = 0;

    const flushBlock = () => {
        if (currentBlock.length === 0) return;

        const trimmedLines = currentBlock.map(l => l.trim());
        const isOnlyBrace = trimmedLines.length === 1 && trimmedLines[0] === "}";

        if (!isOnlyBrace) {
            blocks.push({
                id: blockId++,
                code: currentBlock.join("\n").trim(),
                successors: []
            });
        }

        currentBlock = [];
    };

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        if (trimmed === '') continue;

        // Update brace depth first
        braceDepth += (line.match(/{/g) || []).length;
        braceDepth -= (line.match(/}/g) || []).length;

        currentBlock.push(line);

        const isControl = /^(if|else|for|while|switch|function)\b/.test(trimmed);
        const isEnder = /^(return|break|continue|throw)\b/.test(trimmed);
        const endsSemicolon = trimmed.endsWith(';');
        const nextLine = lines[i + 1]?.trim();

        const shouldFlush = (
            isControl && braceDepth === 1 && currentBlock.length === 1
        ) || (
            isEnder || endsSemicolon
        ) || (
            braceDepth === 0 && (!nextLine || nextLine === '')
        );

        if (shouldFlush) {
            flushBlock();
        }
    }

    // Flush remaining block
    flushBlock();

    console.log(JSON.stringify(blocks, null, 2));
});
