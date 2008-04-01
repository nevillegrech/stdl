using System;
using System.IO;
using EnvDTE;
using EnvDTE80;

namespace STDL.Code
{
    class STDLClassFileGenerator
    {
        private readonly DTE2 _applicationObject;
        private readonly STDLClass _clazz;
        private static readonly string _folder = "stdl";

        public STDLClassFileGenerator(DTE2 applicationObject, STDLClass clazz)
        {
            _applicationObject = applicationObject;
            _clazz = clazz;
        }

        public void CreateFile()
        {
            CreateSTDLFolder();
            string projectPath = _applicationObject.ActiveDocument.Path;
            string filename = Path.Combine(Path.Combine(projectPath, _folder), _clazz.ClassName + ".stdl");
            string tmpFilename = Path.Combine(projectPath, DateTime.Now.Ticks + ".stdl");

            GenerateTemporaryFile(tmpFilename);

            ProjectItem item = _applicationObject.ItemOperations.AddExistingItem(tmpFilename);
            Window window = item.Open(Constants.vsViewKindTextView);
            item.SaveAs(filename);
            window.Activate();
            File.Delete(tmpFilename);
            
            _applicationObject.ActiveDocument.ProjectItem.ContainingProject.Save(_applicationObject.ActiveDocument.ProjectItem.ContainingProject.FullName);
        }

        private void GenerateTemporaryFile(string tmpFilename)
        {
            if (File.Exists(tmpFilename))
            {
                File.Delete(tmpFilename);
            }
            StreamWriter stream = File.CreateText(tmpFilename);

            stream.Write(_clazz.ToString());
            
            stream.Flush();
            stream.Close();
        }

        private void CreateSTDLFolder()
        {
            try
            {
                _applicationObject.ActiveDocument.ProjectItem.ContainingProject.ProjectItems.AddFolder(_folder, "");
            }
            catch
            {
                //Folder already exists
                return;
            }
        }
    }
}
