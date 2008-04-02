using EnvDTE;

namespace STDL
{
    class Events
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
