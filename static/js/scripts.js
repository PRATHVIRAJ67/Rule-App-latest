let lastAST = null;        
let combinedAST = null;   
let BASE_url="https://zeotap-assignment-rule-app-latest.vercel.app"

function displayResult(message) {
    document.getElementById("result").textContent = message;
}

function handleFetchError(error) {
    console.error('Fetch Error:', error);
    displayResult(`Fetch error: ${error.message}`);
}

document.getElementById("ruleForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const ruleString = document.getElementById("ruleInput").value.trim();

    if (!ruleString) {
        displayResult("Please enter a rule string.");
        return;
    }

    try {
        const response = await fetch(`https://zeotap-assignment-rule-app-latest.vercel.app/create_rule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_string: ruleString })
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayResult(`Error: ${errorData.error}`);
            console.error('Error:', errorData);
            return;
        }

        const result = await response.json();
        console.log('AST:', result);
        displayResult(`AST:\n${JSON.stringify(result, null, 2)}`);
        lastAST = result;    
    } catch (error) {
        handleFetchError(error);
    }
});

document.getElementById("combineForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const combineRulesInput = document.getElementById("combineRulesInput").value.trim();

    if (!combineRulesInput) {
        displayResult("Please enter at least one rule string to combine.");
        return;
    }

    const ruleStrings = combineRulesInput.split('\n').map(rule => rule.trim()).filter(rule => rule.length > 0);

    if (ruleStrings.length === 0) {
        displayResult("Please enter valid rule strings (one per line).");
        return;
    }

    try {
        const response = await fetch(`https://zeotap-assignment-rule-app-latest.vercel.app/combine_rules`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rule_strings: ruleStrings })
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayResult(`Error: ${errorData.error}`);
            console.error('Error:', errorData);
            return;
        }

        const result = await response.json();
        console.log('Combined AST:', result);
        displayResult(`Combined AST:\n${JSON.stringify(result, null, 2)}`);
        combinedAST = result;  
    } catch (error) {
        handleFetchError(error);
    }
});

document.getElementById("evalForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const jsonDataInput = document.getElementById("jsonData").value.trim();

    if (!jsonDataInput) {
        displayResult("Please enter user data in JSON format.");
        return;
    }

    let userData;
    try {
        userData = JSON.parse(jsonDataInput);
    } catch (error) {
        displayResult(`Invalid JSON: ${error.message}`);
        console.error('JSON Parse Error:', error);
        return;
    }

    let astToEvaluate = combinedAST || lastAST;

    if (!astToEvaluate) {
        displayResult("No AST available. Please create or combine rules first.");
        return;
    }

    try {
        const response = await fetch(`https://zeotap-assignment-rule-app-latest.vercel.app/evaluate_rule`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ast: astToEvaluate, 
                user_data: userData
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            displayResult(`Error: ${errorData.error}`);
            console.error('Error:', errorData);
            return;
        }

        const result = await response.json();
        console.log('Evaluation Result:', result);
        displayResult(`Evaluation Result: ${JSON.stringify(result, null, 2)}`);
    } catch (error) {
        handleFetchError(error);
    }
});
