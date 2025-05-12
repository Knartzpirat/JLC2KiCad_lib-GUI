# JLC2KiCadLib-GUI

<p style="text-align: center;">



</p>
JLC2KiCadLib-GUI is a UI for [JLC2KiCadLib](https://github.com/TousstNicolas/JLC2KiCad_lib) from [TousstNicolas](TousstNicolas), that generate a component library (symbol, footprint and 3D model) for KiCad from the JLCPCB/easyEDA library. 
This program is currently only developed for Windows (see [Releases](https://github.com/Knartzpirat/JLC2KiCad_lib-GUI/releases)). If you're interested, I can create an executable for Linux. Otherwise, you have the option to build it yourself using the source code.

## Example 



easyEDA origin | KiCad result
---- | ----
![JLCSymbol](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/JLC_Symbol_1.png) | ![KiCadSymbol](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/KiCad_Symbol_1.png)
![JLCFootprint](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/JLC_Footprint_1.png) | ![KiCadFootprint](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/KiCad_Footprint_1.png)
![JLC3Dmodel](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/JLC_3Dmodel.png) | ![KiCad3Dmodel](https://raw.githubusercontent.com/TousstNicolas/JLC2KiCad_lib/master/images/KiCad_3Dmodel.png)

## Installation



## Usage 

My_lib
├── My_footprint_lib
│   ├── My_model_dir
│   │   ├── QFN-24_L4.0-W4.0-P0.50-BL-EP2.7.step
│   │   └── VQFN-48_L7.0-W7.0-P0.50-BL-EP5.5.step
│   ├── QFN-24_L4.0-W4.0-P0.50-BL-EP2.7.kicad_mod
│   └── VQFN-48_L7.0-W7.0-P0.50-BL-EP5.5.kicad_mod
└── My_symbol_lib_dir
    └── My_symbol_lib.kicad_sym
```

Most of those arguments are optional. The only required argument is the JLCPCB part #.

The JLCPCB part # is found in the part info section of every component in the JLCPCB part library. 

By default, the library folder will be created in the execution directory. You can specify an absolute path with the -dir option. 

## Dependencies 

JLC2KiCadLib relies on the [KicadModTree](https://gitlab.com/kicad/libraries/kicad-footprint-generator) framework to generate the footprints. 

## Notes

* Even so I tested the script on a lot of components, be careful and always check the output footprint and symbol.
* I consider this project completed. I will continue to maintain it if a bug report is filed, but I will not develop new functionality in the near future. If you feel that an important feature is missing, please open an issue to discuss it, then you can fork this project with a new branch before submitting a PR. 

## License 

Copyright © 2025 Knartzpirat & TousstNicolas

The code is released under the MIT license
