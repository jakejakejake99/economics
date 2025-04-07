## interactive model: relative demand for skilled labor

this notebook visualizes how the relative demand for high-skilled vs low-skilled labor (H/L) changes with respect to:

- δ: importance of skilled labor in production  
- ρ: elasticity of substitution between labor types  
- w_H, w_L: wages of skilled and unskilled labor  
- φ: productivity shifter favoring unskilled labor  

it uses a ces labor demand function and ipywidgets for interactive exploration.

> inspired by models of skill-biased technical change and ces production functions in labor economics.

---

### visualization preview

- sliders control parameter values, updating both the symbolic equation for H/L and the graph of relative demand.  
equilibrium H/L is displayed with a red dot, and the full curve shows how demand varies across δ.
