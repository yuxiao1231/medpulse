Option Explicit
Dim objShell, objFSO, tempFolder, zipFile, extractFolder, objZip, objDest
Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get current folder (where IExpress extracted us)
tempFolder = objFSO.GetParentFolderName(WScript.ScriptFullName)
zipFile = tempFolder & "\payload.zip"
extractFolder = tempFolder & "\MedPulse_Bin"

' Create extraction folder
If Not objFSO.FolderExists(extractFolder) Then
    objFSO.CreateFolder(extractFolder)
End If

' Unzip using Shell.Application
Set objZip = objShell.NameSpace(zipFile)
Set objDest = objShell.NameSpace(extractFolder)

Dim expectedCount
expectedCount = objZip.Items.Count

' 1024 = do not display a user interface if an error occurs
' 16 = Respond with "Yes to All" for any dialog box that is displayed
' 4 = Do not display a progress dialog box
objDest.CopyHere objZip.Items, 1024 + 16 + 4

' Synchronous wait for extraction to complete
Do Until objDest.Items.Count >= expectedCount
    WScript.Sleep 200
Loop
' Extra buffer time to allow file handles to be released
WScript.Sleep 1000

' Run the program
Dim wshShell
Set wshShell = CreateObject("WScript.Shell")
' Run MedPulse.exe and wait for it to exit
wshShell.Run """" & extractFolder & "\MedPulse.exe""", 1, True

' Clean up
On Error Resume Next
objFSO.DeleteFolder extractFolder, True
On Error GoTo 0
