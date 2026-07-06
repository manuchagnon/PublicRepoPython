from enum import Flag, auto, EnumMeta

"""
Decorator to use inside auto rig code of module
Its use is to specify if a module method :
    - UseType.UNIQUE = has to be used one time only
    - UseType.MULTIPLE = can be used several times or one 
    - UseType.NECESSARY = is necessary
    - UseType.UNNECESSARY = is not necessary
    - UseType.FORBIDDEN = is forbidden to use  (I don't know if I will need this sometime) 
If not specified, use the flag UseType.UNSPECIFIED or nothing

UseType.EXCLUDE_1 = means that it can be used but it will exclude the use of other functions with UseType.EXCLUDE_1
Same with EXCLUDE_1, EXCLUDE_2, EXCLUDE_3
This works as slots
UseType.EXCLUDING contains all slots available

"""
class AutoExtendMeta(EnumMeta):

    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)
        type.__setattr__(cls, "_custom_members_", [])
        type.__setattr__(cls, "_excluding_value_", 0)
        return cls

    def _next_flag_value_(cls):
        existing = [m._value_ for m in cls._member_map_.values() if isinstance(m._value_, int)]
        return max(existing, default=0) * 2 or 1

    def __getattr__(cls, name: str):
        if name.isupper():
            if not name in cls._member_map_: # if it doesn't exist yet
                obj = object.__new__(cls)
                obj._value_ = cls._next_flag_value_() # custom generating of next bitwise value, mimic Flag auto() behavior
                obj._name_ = name
                cls._value2member_map_[obj._value_] = obj
                cls._member_map_[name] = obj
                cls._member_names_.append(name)
                cls._custom_members_.append(obj)

                if hasattr(cls, "_flag_mask_"):
                    cls._flag_mask_ |= obj._value_
                if hasattr(cls, "_singles_mask_"):
                    cls._singles_mask_ |= obj._value_
                if hasattr(cls, "_all_bits_"):
                    cls._all_bits_ |= obj._value_

                # Binary accumulation while getting past the Enum protection
                # Storing newly created attributes in cls._excluding_value_
                type.__setattr__(cls, "_excluding_value_", cls._excluding_value_ | obj._value_)

                return obj
            else:
                return cls[name]

        raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

    @property
    def EXCLUDING(cls):
        # Reconstruit le membre Flag à la volée depuis la valeur accumulée
        return cls(cls._excluding_value_)


class UseType(Flag, metaclass=AutoExtendMeta):

    UNSPECIFIED = auto()

    MULTIPLE = auto()
    UNIQUE = auto()

    NECESSARY = auto()
    UNNECESSARY = auto()

    FORBIDDEN = auto()

def use(use_type: UseType=UseType.UNSPECIFIED):
    def inner(fun):
        def wrapped(*args, **kwargs):
            return fun(*args, **kwargs)
        wrapped.use = use_type
        return wrapped
    return inner

if __name__ == '__main__':
    print("-"*50)
    # Script to use UseType excluding behavior for Auto-rig Ui
    use0 = UseType.UNIQUE
    use1 = UseType.EXCLUDE_1
    use2 = UseType.EXCLUDE_2 | UseType.MULTIPLE
    use3 = UseType.BABA | UseType.EXCLUDE_2

    def exe():
        excluded = []
        for use in [use0, use1, use2, use3]:
            # if the use contains an exclusive slot
            if use & UseType.EXCLUDING:
                # adds this exclusive slot inside the list of excluded slots, if it's not already inside
                print("excluding", use.name)
                excluded.append(use & UseType.EXCLUDING)
            else:
                print("do nothing with", use.name)

        excluded_names = [excl.name for excl in excluded]
        print("I excluded these slots", excluded_names)
    exe()