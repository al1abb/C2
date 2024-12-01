# Add-Type -AssemblyName Microsoft.VisualBasic
# [Microsoft.VisualBasic.Interaction]::MsgBox("Do you want to continue?", [Microsoft.VisualBasic.MsgBoxStyle]::YesNo + [Microsoft.VisualBasic.MsgBoxStyle]::Question, "Confirm Action")

# Add-Type -AssemblyName System.Windows.Forms

# # Create a new form
# $form = New-Object System.Windows.Forms.Form
# $form.Text = "Confirmation"
# $form.Size = New-Object System.Drawing.Size(300, 150)

# # Add a label to the form
# $label = New-Object System.Windows.Forms.Label
# $label.Text = "Are you gay?"
# $label.AutoSize = $true
# $label.Location = New-Object System.Drawing.Point(50, 20)
# $form.Controls.Add($label)

# # Add a "YesYes" button
# $yesYesButton = New-Object System.Windows.Forms.Button
# $yesYesButton.Text = "Yes"
# $yesYesButton.Location = New-Object System.Drawing.Point(50, 60)
# $yesYesButton.Add_Click({ $form.Tag = "Yes"; $form.Close() })
# $form.Controls.Add($yesYesButton)

# # Add a "No" button
# $noButton = New-Object System.Windows.Forms.Button
# $noButton.Text = "Yes"
# $noButton.Location = New-Object System.Drawing.Point(150, 60)
# $noButton.Add_Click({ $form.Tag = "Yes"; $form.Close() })
# $form.Controls.Add($noButton)

# # Show the form
# $form.ShowDialog()

# # Return the result
# $result = $form.Tag
# Write-Host "You selected: $result"

# # Open the URL in the default browser
# Start-Process -FilePath "cmd" -ArgumentList "/c start https://updatefaker.com/windows11/index.html" -WindowStyle Hidden

# # Wait a few seconds for the browser to load
# Start-Sleep -Seconds 2

# # Simulate the F11 key press for full-screen mode
# Add-Type -AssemblyName System.Windows.Forms
# [System.Windows.Forms.SendKeys]::SendWait("{F11}")