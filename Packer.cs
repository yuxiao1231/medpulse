using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.IO.Compression;

namespace MedPulsePacker
{
    class Program
    {
        static void Main(string[] args)
        {
            string tempDir = Path.Combine(Path.GetTempPath(), "MedPulse_" + Guid.NewGuid().ToString().Substring(0, 8));
            try
            {
                Directory.CreateDirectory(tempDir);
                using (Stream resStream = Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip"))
                {
                    if (resStream == null)
                    {
                        return;
                    }
                    using (ZipArchive archive = new ZipArchive(resStream, ZipArchiveMode.Read))
                    {
                        foreach (ZipArchiveEntry entry in archive.Entries)
                        {
                            string destPath = Path.GetFullPath(Path.Combine(tempDir, entry.FullName));
                            if (!destPath.StartsWith(tempDir, StringComparison.OrdinalIgnoreCase)) continue;
                            
                            if (string.IsNullOrEmpty(entry.Name) || entry.FullName.EndsWith("/"))
                            {
                                Directory.CreateDirectory(destPath);
                            }
                            else
                            {
                                Directory.CreateDirectory(Path.GetDirectoryName(destPath));
                                entry.ExtractToFile(destPath, true);
                            }
                        }
                    }
                }

                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = Path.Combine(tempDir, "MedPulse.exe");
                psi.WorkingDirectory = tempDir;
                psi.UseShellExecute = false;

                using (Process p = Process.Start(psi))
                {
                    p.WaitForExit();
                }
            }
            catch (Exception)
            {
                // Silent catch
            }
            finally
            {
                try
                {
                    if (Directory.Exists(tempDir))
                    {
                        Directory.Delete(tempDir, true);
                    }
                }
                catch { }
            }
        }
    }
}
