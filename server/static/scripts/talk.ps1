# TODO: Make this accept a parameter for the text to speak (Like with toast.ps1)

Function Speak-Text($Text) { Add-Type -AssemblyName System.speech; $TTS = New-Object System.Speech.Synthesis.SpeechSynthesizer; $TTS.Speak($Text) }
Speak-Text "Hello World!"
Exit