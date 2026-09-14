// Shared room entry views let both modes open at a comparable camera pose.
export const roomViewpoints:Record<string,{position:[number,number,number];target:[number,number,number]}>={
  "living": {
    "position": [
      6.15,
      1.58,
      1.35
    ],
    "target": [
      4.0,
      1.3,
      4.0
    ]
  },
  "bed1": {
    "position": [
      5.35,
      1.58,
      -1.8
    ],
    "target": [
      5.5,
      1.3,
      -4.0
    ]
  },
  "bed2": {
    "position": [
      1.6,
      1.58,
      -1.15
    ],
    "target": [
      0.6,
      1.3,
      -2.9
    ]
  },
  "bed3": {
    "position": [
      1.75,
      1.58,
      6.35
    ],
    "target": [
      0.2,
      1.3,
      6.5
    ]
  },
  "bed4": {
    "position": [
      1.55,
      1.58,
      11.0
    ],
    "target": [
      0.1,
      1.3,
      11.4
    ]
  },
  "bath1": {
    "position": [
      5.25,
      1.56,
      7.4
    ],
    "target": [
      3.9,
      1.2,
      6.9
    ]
  },
  "bath2": {
    "position": [
      5.25,
      1.56,
      5.15
    ],
    "target": [
      3.9,
      1.2,
      5.8
    ]
  },
  "hall": {
    "position": [
      6.55,
      1.58,
      5.9
    ],
    "target": [
      6.4,
      1.3,
      2.8
    ]
  },
  "deck": {
    "position": [
      1.35,
      1.58,
      3.35
    ],
    "target": [
      1.0,
      1.15,
      2.45
    ]
  }
};
