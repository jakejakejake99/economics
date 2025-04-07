# cournot competition interactive app

this script launches an interactive tkinter-based gui for visualizing strategic firm behavior in oligopoly models. it allows users to explore the best-response functions and equilibrium outcomes under different competition scenarios.

## features

- visualize best-response curves for firm 1 and firm 2  
- adjust linear best-response parameters using sliders or text boxes  
- toggle iso-profit contours and cartel regions  
- supports multiple game-theoretic scenarios:
  - cournot (simultaneous move)
  - stackelberg (firm 1 leads)
  - stackelberg (firm 2 leads)
  - collusion (joint profit-maximization)
- animate iterative best-responses (cobweb path) to show convergence  
- displays equilibrium point for each scenario  

## requirements

- python 3  
- tkinter  
- sympy  
- numpy  
- matplotlib  

## usage

run the script directly:

```bash
python cournot_gui.py
