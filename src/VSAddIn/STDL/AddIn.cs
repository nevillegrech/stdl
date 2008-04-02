using EnvDTE;
using EnvDTE80;
using System.Windows.Forms;

namespace STDL
{
    class AddIn
    {
        private static DTE2 _application;

        public static void CompileOnBuild(ProjectItem item)
        {
            item.DTE.Events.BuildEvents.OnBuildBegin += (BuildEvents_OnBuildBegin);
        }

        static void BuildEvents_OnBuildBegin(vsBuildScope Scope, vsBuildAction Action)
        {
            Compiler.Compile("");
        }

        public static void AttachEventsToExisting(DTE2 application)
        {
            _application = application;
            _application.Events.SolutionEvents.Opened += new _dispSolutionEvents_OpenedEventHandler(SolutionEvents_Opened);
            _application.Events.get_WindowEvents(null).WindowCreated += new _dispWindowEvents_WindowCreatedEventHandler(AddIn_WindowCreated);
            _application.Events.get_DocumentEvents(null).DocumentOpened += new _dispDocumentEvents_DocumentOpenedEventHandler(AddIn_DocumentOpened);
            _application.Events.get_DocumentEvents(null).DocumentSaved += new _dispDocumentEvents_DocumentSavedEventHandler(AddIn_DocumentSaved);
        }

        static void AddIn_DocumentOpened(Document Document)
        {
            MessageBox.Show("AddIn_DocumentOpened");
        }

        static void AddIn_WindowCreated(Window Window)
        {
            MessageBox.Show("AddIn_WindowCreated");
        }

        static void SolutionEvents_Opened()
        {
            foreach (Document document in _application.Documents)
            {
                ((DTE2)_application).Events.get_DocumentEvents(document).DocumentSaved += new _dispDocumentEvents_DocumentSavedEventHandler(AddIn_DocumentSaved);
            }
        }

        static void AddIn_DocumentSaved(Document Document)
        {
            MessageBox.Show("AddIn_DocumentSaved");
        }

    }
}
