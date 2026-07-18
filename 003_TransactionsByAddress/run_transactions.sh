#!/bin/bash

# Ejecutar la obtención de los SBP
python3 viteTxs.py --vaddr vite_0000000000000000000000000000000000000004d28108e76b --nodeIP 85.190.246.211 --name SBP --mode actualizar

# Ejecutar la obtención de Quota
python3 viteTxs.py --vaddr vite_0000000000000000000000000000000000000003f6af7459b9 --nodeIP 85.190.246.211 --name Quota --mode actualizar

# Ejecutar la la otención de vitex
python3 viteTxs.py --vaddr vite_0000000000000000000000000000000000000006e82b8ba657 --nodeIP 85.190.246.211 --name vitex --mode actualizar

# Ejecutar la la otención de los rewards de los FullNodes
python3 viteTxs.py --vaddr vite_1737bb7abc4883cc2f415a804f80274d3a725a68a5bee5bad3 --nodeIP 85.190.246.211 --name FullnodeDistribution --mode actualizar

# Ejecutar la la otención de los rewards de los FullNodesOLD
python3 viteTxs.py --vaddr vite_86f729c9b7dda636e46b7ae738785be87f71390f532828ace9 --nodeIP 85.190.246.211 --name OLDFullnodeDistribution --mode actualizar

# Ejecutar la la otención de los staked FullNodes Daily
python3 viteTxs.py --vaddr vite_8cf2663cc949442db2d3f78f372621733292d1fb0b846f1651 --nodeIP 85.190.246.211 --name FullNodesDaily --mode actualizar

# Ejecutar la la otención de los staked FullNodes Daily
python3 viteTxs.py --vaddr vite_000000000000000000000000000000000000000595292d996d --nodeIP 85.190.246.211 --name issueContract --mode actualizar



# python3 viteTxs.py --vaddr vite_4275b7acc267969e830e235af512bcb966e44de16f2352266f --nodeIP 85.190.246.211 --name whaleVGATE 
