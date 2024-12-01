Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Windows.Forms;

public class BSOD
{
    public static void Show()
    {
        Form form = new Form();
        form.Text = "STOP: 0x0000007B";
        form.BackColor = Color.Blue;
        form.WindowState = FormWindowState.Maximized;
        form.FormBorderStyle = FormBorderStyle.None;
        form.StartPosition = FormStartPosition.CenterScreen;
        
        Label label = new Label();
        label.Text = "A problem has been detected and Windows has been shut down to prevent damage to your computer.\n\nSTOP: 0x0000007B\n\n\n";
        label.ForeColor = Color.White;
        label.Font = new Font("Arial", 20, FontStyle.Bold);
        label.AutoSize = true;
        label.Location = new Point(form.Width / 4, form.Height / 4);
        
        form.Controls.Add(label);
        form.ShowDialog();
    }
}
"@
[BSOD]::Show()