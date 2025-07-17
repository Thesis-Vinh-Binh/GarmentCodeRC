import numpy as np
import pygarment as pyg

from assets.garment_programs.base_classes import StackableSkirtComponent
from assets.garment_programs.skirt_paneled import SkirtPanel

class AoDaiFlap(StackableSkirtComponent):
    """Simple 2 panel ao dai flap"""
    def __init__(self, body, design, tag='', length=None, rise=None, slit=True, top_ruffles=True, min_len=5) -> None:
        super().__init__(body, design, tag)

        design = design['skirt']

        self.rise = design['rise']['v'] if rise is None else rise
        waist, hip_line, back_waist = self.eval_rise(self.rise)

        # Force from arguments if given
        if length is None:
            length = hip_line + design['length']['v'] * body['_leg_length']  # Depends on leg length

        # NOTE: with some combinations of rise and length parameters length may become too small/negative
        # Hence putting a min positive value here
        length = max(length, min_len)

        self.front = SkirtPanel(
            f'skirt_front_{tag}' if tag else 'skirt_front', 
            waist_length=waist - back_waist, 
            length=length,
            ruffles=design['ruffle']['v'] if top_ruffles else 1,   # Only if on waistband
            flare=design['flare']['v'],
            bottom_cut=design['bottom_cut']['v'] * design['length']['v'] if slit else 0,
            match_top_int_to=(body['waist'] - body['waist_back_width'])
        ).translate_to([0, body['_waist_level'], 25])
        self.back = SkirtPanel(
            f'skirt_back_{tag}'  if tag else 'skirt_back', 
            waist_length=back_waist, 
            length=length,
            ruffles=design['ruffle']['v'] if top_ruffles else 1,   # Only if on waistband
            flare=design['flare']['v'],
            bottom_cut=design['bottom_cut']['v'] * design['length']['v'] if slit else 0,
            match_top_int_to=body['waist_back_width']
        ).translate_to([0, body['_waist_level'], -20])

        self.stitching_rules = pyg.Stitches(
        )

        # Reusing interfaces of sub-panels as interfaces of this component
        self.interfaces = {
            'top_f': self.front.interfaces['top'],
            'top_b': self.back.interfaces['top'],
            'top': pyg.Interface.from_multiple(
                self.front.interfaces['top'], self.back.interfaces['top']
            ),
            'bottom_f': self.front.interfaces['bottom'],
            'bottom_b': self.back.interfaces['bottom'],
            'bottom': pyg.Interface.from_multiple(
                self.front.interfaces['bottom'], self.back.interfaces['bottom']
            )
        }

    def length(self):
        return self.front.length()