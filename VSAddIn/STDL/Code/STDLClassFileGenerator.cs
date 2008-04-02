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
            ProjectItem folder = CreateSTDLFolder();

            string projectPath = _applicationObject.ActiveDocument.Path;
            string filename = Path.Combine(Path.Combine(projectPath, _folder), _clazz.ClassName + ".stdl");

            GenerateFile(filename);

            ProjectItem item = folder.ProjectItems.AddFromFile(filename);
            Window window = item.Open(Constants.vsViewKindTextView);

            Events.CompileOnBuild(item);

            _applicationObject.ActiveDocument.ProjectItem.ContainingProject.Save(_applicationObject.ActiveDocument.ProjectItem.ContainingProject.FullName);
            window.Activate();
        }

        private void GenerateFile(string filename)
        {
            if (File.Exists(filename))
            {
                File.Delete(filename);
            }
            StreamWriter stream = File.CreateText(filename);

            stream.Write(_clazz.ToString());

            stream.Flush();
            stream.Close();
        }

        private ProjectItem CreateSTDLFolder()
        {
            foreach (ProjectItem projectItem in _applicationObject.ActiveDocument.ProjectItem.ContainingProject.ProjectItems)
            {
                if (_folder.Equals(projectItem.Name))
                {
                    return projectItem;
                }
            }
            return _applicationObject.ActiveDocument.ProjectItem.ContainingProject.ProjectItems.AddFolder(_folder, "");
        }

    }
}
