from copy import deepcopy
from assets.garment_programs.ao_dai_flap import AoDaiFlap
import pygarment as pyg
from assets.garment_programs.bodice import BodiceHalf

class AoDai(pyg.Component):
    """Ao Dai"""

    def __init__(self, body, design, fitted=True) -> None:
        name_with_params = f"{self.__class__.__name__}"
        super().__init__(name_with_params)

        design = self.eval_dep_params(design)

        self.right = BodiceHalf(f'right', body, design, fitted=fitted)
        self.left = BodiceHalf(f'left', body, design, fitted=fitted).mirror()
        
        # Adjust interface ordering for correct connectivity
        self.interfaces = {   # Bottom connection
            'bottom': pyg.Interface.from_multiple(
                self.right.interfaces['f_bottom'].reverse(),
                self.left.interfaces['f_bottom'],
                self.left.interfaces['b_bottom'].reverse(),
                self.right.interfaces['b_bottom'],)
        }
        
        if fitted:
            shirt_bottom_width = self.right.ftorso.get_width(0) + self.left.ftorso.get_width(0)
        else:
            shirt_bottom_width = self.right.half_bottom_width + self.left.half_bottom_width

        self.flap = AoDaiFlap(body, design, top_width=shirt_bottom_width, top_length=body['_waist_level'] - self.right.ftorso.get_width(0) / 2)
        

        self.stitching_rules = pyg.Stitches(
            (self.right.interfaces['front_in'],
                                        self.left.interfaces['front_in']),
            (self.right.interfaces['back_in'],
                                     self.left.interfaces['back_in']),
            (self.flap.interfaces['top'],
                                     self.interfaces['bottom'])
        )


        

    def eval_dep_params(self, design):
        # NOTE: Support for full collars with partially strapless top
        # or combination of paneled collar styles
        # requres further development
        # TODOLOW enable this one to work
        if design['left']['enable_asym']['v']:
            # Force no collars since they are not compatible with each other
            design = deepcopy(design)
            design['collar']['component']['style']['v'] = None
            design['left']['collar']['component'] = dict(style=dict(v=None))
            
            # Left-right design compatibility 
            design['left']['shirt'].update(length={})
            design['left']['shirt']['length']['v'] = design['shirt']['length']['v']
            
            design['left']['collar'].update(fc_depth={}, bc_depth={})
            design['left']['collar']['fc_depth']['v'] = design['collar']['fc_depth']['v']
            design['left']['collar']['bc_depth']['v'] = design['collar']['bc_depth']['v']

        return design

    def length(self):
        return self.right.length()