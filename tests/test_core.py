import math, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'software'))
import scilla_passive_core as s
class TestCore(unittest.TestCase):
    def test_scan_period(self): self.assertAlmostEqual(s.SCAN_PERIOD,2.5,places=9)
    def test_horizon_positive(self): self.assertGreater(s.H_TX_TGT,20)
    def test_pulse_sigma_order(self): self.assertLess(s.base_meas_sigma('S1'),s.base_meas_sigma('L'))
    def test_bistatic_zero_at_target_on_tx(self):
        import numpy as np
        rx=np.array([0.,0.]); tx=np.array([1000.,0.]); x=np.array([1000.,0.,0.,0.])
        self.assertAlmostEqual(s.h(x,tx,rx),0.0,places=6)
    def test_paired_world(self):
        rr=s.run_world_all(12345,duration=10,n_donors=4)
        self.assertEqual(len(rr),len(s.POLICIES))
if __name__=='__main__': unittest.main()
