using EnvDTE;

namespace STDL
{
    class AddIn
    {
        public static void CompileOnBuild(ProjectItem item)
        {
            item.DTE.Events.BuildEvents.OnBuildBegin += (BuildEvents_OnBuildBegin);
        }

        static void BuildEvents_OnBuildBegin(vsBuildScope Scope, vsBuildAction Action)
        {
            Compiler.Compile("");
        }

    }
}
