using System;
using EnvDTE;
using EnvDTE80;
using Extensibility;
using Microsoft.VisualStudio.CommandBars;
using STDL.Code;

namespace STDL
{
    /// <summary>The object for implementing an Add-in.</summary>
    /// <seealso class='IDTExtensibility2' />
    public class Connect : IDTExtensibility2, IDTCommandTarget
    {
        private EnvDTE.AddIn _addInInstance;
        private DTE2 _applicationObject;

        #region IDTCommandTarget Members

        /// <summary>Implements the QueryStatus method of the IDTCommandTarget interface. This is called when the command's availability is updated</summary>
        /// <param term='commandName'>The name of the command to determine state for.</param>
        /// <param term='neededText'>Text that is needed for the command.</param>
        /// <param term='status'>The state of the command in the user interface.</param>
        /// <param term='commandText'>Text requested by the neededText parameter.</param>
        /// <seealso class='Exec' />
        public void QueryStatus(string commandName, vsCommandStatusTextWanted neededText, ref vsCommandStatus status,
                                ref object commandText)
        {
            status = vsCommandStatus.vsCommandStatusSupported;
            if (neededText == vsCommandStatusTextWanted.vsCommandStatusTextWantedNone)
            {
                if (commandName == "STDL.Connect.GenerateClassCode" &&
                        _applicationObject.ActiveDocument != null && _applicationObject.ActiveDocument.ProjectItem != null &&
                        _applicationObject.ActiveDocument.ProjectItem.FileCodeModel != null && 
                        _applicationObject.ActiveDocument.ProjectItem.FileCodeModel.CodeElements.Count > 0)
                {
                    status |= vsCommandStatus.vsCommandStatusEnabled;
                }
            }
        }

        /// <summary>Implements the Exec method of the IDTCommandTarget interface. This is called when the command is invoked.</summary>
        /// <param term='commandName'>The name of the command to execute.</param>
        /// <param term='executeOption'>Describes how the command should be run.</param>
        /// <param term='varIn'>Parameters passed from the caller to the command handler.</param>
        /// <param term='varOut'>Parameters passed from the command handler to the caller.</param>
        /// <param term='handled'>Informs the caller if the command was handled or not.</param>
        /// <seealso class='Exec' />
        public void Exec(string commandName, vsCommandExecOption executeOption, ref object varIn, ref object varOut,
                         ref bool handled)
        {
            handled = false;
            if (executeOption == vsCommandExecOption.vsCommandExecOptionDoDefault)
            {
                if (commandName == "STDL.Connect.GenerateClassCode")
                {
                    handled = true;
                    GenerateClassCode();
                    return;
                }
            }
        }

        private void GenerateClassCode()
        {
            STDLClassFileGenerator fileGenerator = new STDLClassFileGenerator(_applicationObject, new STDLClass(_applicationObject.ActiveDocument.ProjectItem.FileCodeModel));
            fileGenerator.CreateFile();   
        }
        #endregion

        #region IDTExtensibility2 Members

        /// <summary>Implements the OnConnection method of the IDTExtensibility2 interface. Receives notification that the Add-in is being loaded.</summary>
        /// <param term='application'>Root object of the host application.</param>
        /// <param term='connectMode'>Describes how the Add-in is being loaded.</param>
        /// <param term='addInInst'>Object representing this Add-in.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnConnection(object application, ext_ConnectMode connectMode, object addInInst, ref Array custom)
        {
            _applicationObject = (DTE2) application;
            _addInInstance = (EnvDTE.AddIn) addInInst;

            if (connectMode == ext_ConnectMode.ext_cm_AfterStartup)
            {
                AddIn.AttachEventsToExisting(_applicationObject);
            }
            else
            {
                if (connectMode == ext_ConnectMode.ext_cm_UISetup)
                {
                    object[] contextGUIDS = new object[] {};
                    Commands2 commands = (Commands2) _applicationObject.Commands;

                    CommandBar menuBarCommandBar = ((CommandBars) _applicationObject.CommandBars)["Code Window"];

                    try
                    {
                        Command command =
                            commands.AddNamedCommand2(_addInInstance, "GenerateClassCode", "Generate STDL",
                                                      "Generates a STDL file for the current class",
                                                      true, 0, ref contextGUIDS,
                                                      (int) vsCommandStatus.vsCommandStatusSupported +
                                                      (int) vsCommandStatus.vsCommandStatusEnabled,
                                                      (int) vsCommandStyle.vsCommandStylePictAndText,
                                                      vsCommandControlType.vsCommandControlTypeButton);

                        if ((command != null) && (menuBarCommandBar != null))
                        {
                            command.AddControl(menuBarCommandBar, 1);
                        }
                    }
                    catch (ArgumentException)
                    {
                    }
                }
            }
        }

        /// <summary>Implements the OnDisconnection method of the IDTExtensibility2 interface. Receives notification that the Add-in is being unloaded.</summary>
        /// <param term='disconnectMode'>Describes how the Add-in is being unloaded.</param>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnDisconnection(ext_DisconnectMode disconnectMode, ref Array custom)
        {
        }

        /// <summary>Implements the OnAddInsUpdate method of the IDTExtensibility2 interface. Receives notification when the collection of Add-ins has changed.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />		
        public void OnAddInsUpdate(ref Array custom)
        {
        }

        /// <summary>Implements the OnStartupComplete method of the IDTExtensibility2 interface. Receives notification that the host application has completed loading.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnStartupComplete(ref Array custom)
        {
        }

        /// <summary>Implements the OnBeginShutdown method of the IDTExtensibility2 interface. Receives notification that the host application is being unloaded.</summary>
        /// <param term='custom'>Array of parameters that are host application specific.</param>
        /// <seealso class='IDTExtensibility2' />
        public void OnBeginShutdown(ref Array custom)
        {
        }

        #endregion

    }

}