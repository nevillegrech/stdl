using EnvDTE;

namespace STDL.Code
{
    public class STDLType
    {
        private readonly CodeTypeRef _type;

        public STDLType(CodeTypeRef type)
        {
            _type = type;
        }

        public override string ToString()
        {
            return _type.AsString;
        }

        public string FullName()
        {
            return _type.AsFullName;
        }

        public string DefaultValue()
        {
            switch(_type.TypeKind)
            {
                case vsCMTypeRef.vsCMTypeRefBool:
                    return "<% true %>";
                case vsCMTypeRef.vsCMTypeRefDecimal:
                case vsCMTypeRef.vsCMTypeRefDouble:
                case vsCMTypeRef.vsCMTypeRefFloat:
                case vsCMTypeRef.vsCMTypeRefLong:
                    return "0.0";
                case vsCMTypeRef.vsCMTypeRefInt:
                case vsCMTypeRef.vsCMTypeRefShort:
                    return "0";
                case vsCMTypeRef.vsCMTypeRefString:
                    return "<% \"\" %>";
                default:
                    return "<% new " + _type.AsFullName + "() %>";
            }
        }
    }
}
