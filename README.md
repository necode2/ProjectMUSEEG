# ProjectMUSEEG
*Welcome to Project MUSEEG! (Pronounced Muse-EGG) * </br></br>
***Project A*** </br> 
*Music is already known to help with anxiety, focus, and relaxation—but what if it could be tailored to an individual’s brain activity? Brainwaves provide measurable indicators of emotional states like stress, restlessness, and calm. By collecting EEG data and training a neural network, I aim to create a system that detects these emotional states and generates personalized music designed to counteract them. The long-term goal is to explore applications in mental health, where this system could be used in hospitals, therapy settings, or for personal well-being. Since neurotechnology isn’t one-size-fits-all, this research is a step toward more personalized solutions in brain-music interaction.* </br></br>
***Project B***
*Ever wondered if someone could hear your thoughts? While we’re not at the point of translating thoughts into words, we can start by turning brain activity into music. Since music is a universal language, this research will explore how EEG data can be converted into sound patterns. By mapping electrical brain signals to musical structures, we lay the groundwork for future nonverbal communication systems. This could eventually evolve into a tool for individuals who struggle with verbal communication, but for now, the focus is on understanding the underlying brain-music relationship.* </br></br>
## Phase 1: Initial Research
*[Bibliography](https://docs.google.com/document/d/126_Q5-wPVYQXYX758TkZR0ndfYQ_7DFlI9uJoeaBVlY/edit?usp=sharing) of useful resources.*
## Phase 2: Hardware 
<div align="center">
<img src="README_IMGS/assembly.gif"/></div>

*Materials unboxing*
|------|

|Material Link                       | What's Included                                                                   | Cost                        |
| --------                           | -------                                                                           | -------                     |
| [Ultracortex "Mark IV" EEG Headset](https://shop.openbci.com/products/ultracortex-mark-iv?variant=23280741699)  | <ul><li> EEG nodes</li><li>Ear clips</li><li>Screws</li><li>Ribbon Cables</li></ul> |$900                         |
| [Daisy + Cyton BioSensing Board](https://shop.openbci.com/products/cyton-daisy-biosensing-boards-16-channel?variant=38959256526)    | <ul><li>Cyton+Daisy board (able to receive data from 16 different channels/points on brain)</li><li>Rechargeable Lithium Battery</li><li>Charging pack (for battery)</li><li>Programmable Dongle (Bluetooth communication)</li><li>Y-splitter cable</li><li>Board cover</li></ul> | $2100|
|[USB-A to USB-C Converter](https://www.bestbuy.com/site/insignia-usb-c-to-usb-adapter-black/6473492.p?skuId=6473492&extStoreId=46&utm_source=feed&ref=212&loc=18670532085&gad_source=1&gad_campaignid=18673989082&gbraid=0AAAAAD-ORIiROXi48bwZ1xsDqw0y9IgxL&gclid=Cj0KCQjwjo7DBhCrARIsACWauSmR3vUUhmtopa0tZ__U4yZM3AUu9UiuOb3mSAOf0FKv1AXDpcI0BTkaAo3EEALw_wcB&gclsrc=aw.ds) | <ul><li>USB-A to USB-C Converter</li></ul> | $10 |
|[Gorilla Glue](https://g.co/kgs/9oacW73) | <ul><li>Super Glue</li></ul>| $7 |

***Assembly of the headset is relatively simple, there are a few things to keep in mind:***
<ul><li>Assembly will take 24hrs+ because you will need to superglue in the inserts and wait for them to set overnight</li>
<li>ALWAYS make sure to check the polarity, ada fruit batteries only have one way to insert them so make sure the *red wire* aligns with the positive port and the the *black wire* aligns with the negative port when plugging into the Cyton board</li>
<li>The new design of the board covers/mounts does NOT have the three holes on either side, instead they are long oval shaped opening. They are helpful for custom positioning on to the EEG frame but a bit tricky to level. If you would like the original case, you can always 3D print it by using the <a href="https://github.com/openbci-archive/Docs/blob/master/assets/MarkIV/STL_Directory/M4%20Board_Mount.stl">STL provided on the OpenBCI website</a>.</li>
<li>This assembly video does not follow the OpenBCI documentation, it has some inconsistencies with node placement and wire color cooridination. It also does not show how to connect the wires to the Cyton+Daisy boards. When I went through the assembly process the video was helpful to me inorder to have a step by step, narrated assembly, but I did find myself using the <a href="https://docs.openbci.com/AddOns/Headwear/MarkIV/">documentation</a> and the <a href="https://docs.openbci.com/assets/images/1020-8a20d1014a755a8d1d968751ddc3b908.jpg">node placement 10-20 system diagram the most</a>.</li>
<li>I also have a mac with ONLY USB-C ports, and I could not find a source that explained what converter I needed for the bluetooth dongle. WIth some help from BestBuy, it is a USB-A without the protective casing. </li></ul>

***

![](README_IMGS/final.png)
*Finalized assembly of EEG Ultracortex Headset*
|------|

***

## Phase 3: Implementing Software
*connecting with the free OpenBCI Software*
*retrieving, and storing data*
*analyzing data with Neural Network*
*maybe creating simole program utilizing this information*
# Project A: Musical Therapy
## Phase 4: Collecting Data (relevant to project)
## Phase 5: Analyzing Data (relevant to project)
# Project B: Brain Wave to Music Interpretation
## Phase 4: Collecting Data (relevant to project)
## Phase 5: Analyzing Data (relevant to project)
