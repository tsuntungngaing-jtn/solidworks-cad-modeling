"""Small, explicit SolidWorks COM contracts. Import has no application side effects."""
from pathlib import Path
from math import isfinite

def r8(values):
    """Create double SAFEARRAY, avoiding ambiguous VARIANT-of-VARIANT arrays."""
    import pythoncom
    import win32com.client as com
    numbers = tuple(float(v) for v in values)
    if not all(isfinite(v) for v in numbers):
        raise ValueError('SAFEARRAY values must be finite')
    return com.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, numbers)

def translation_data(x_mm, y_mm, z_mm):
    xyz = [float(v)/1000 for v in (x_mm,y_mm,z_mm)]
    if not all(isfinite(v) for v in xyz):
        raise ValueError('Translation must be finite')
    return [1.,0.,0.,0.,1.,0.,0.,0.,1.,*xyz,1.,0.,0.,0.]

def assert_transform(actual, expected, tolerance=1e-10):
    a, e = list(actual), list(expected)
    if len(a)!=16 or len(e)!=16 or not isfinite(tolerance) or tolerance<0:
        raise ValueError('Expected two 16-value transforms and nonnegative tolerance')
    if any(not isfinite(float(x)) or not isfinite(float(y)) or abs(x-y)>tolerance
           for x,y in zip(a,e)):
        raise ValueError(f'Transform readback mismatch: actual={a}, expected={e}')

def ensure_configuration(model, current_name, target):
    """current_name is a callback that reacquires ConfigurationManager/active config."""
    if target not in (model.GetConfigurationNames() or ()):
        raise ValueError(f'Missing configuration: {target}')
    before = current_name()
    result = None if before==target else model.ShowConfiguration2(target)
    after = current_name()
    if after!=target:
        raise RuntimeError(f'Configuration switch failed: target={target}, actual={after}, API={result}')
    return {'already_active':before==target,'api_result':result,'active':after}

def find_equation(equations, variable):
    target = '"'+variable+'"'
    matches = [i for i,e in enumerate(equations) if e.split('=',1)[0].strip()==target]
    if len(matches)!=1:
        raise ValueError(f'Expected one equation for {variable}, found {len(matches)}')
    return matches[0]

def native_files(directory):
    """Top-level native CAD only; excludes SolidWorks lock files."""
    return sorted((p for p in Path(directory).iterdir()
                   if p.is_file() and not p.name.startswith('~$')
                   and p.suffix.lower() in {'.sldprt','.sldasm'}),key=lambda p:p.name)
