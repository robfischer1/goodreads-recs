import {createTheme, responsiveFontSizes} from '@mui/material/styles'

const _paynesGray = '#626E75'
const _onyx = '#3A3C40'
const _khaki = '#B4AE9C'
const _battleshipGray = '#8E8F86'
const _Gray = '#7E7C77'

// Khaki
// default: '#FCF5E5',
// Navy
// default: '#000010',
let theme = createTheme({
  palette: {
    primary: {
      main: _paynesGray
    },
    secondary: {
      main: _onyx
    },
    tertiary: {
      main: '#FFA970',
      contrastText: "#FFF"
    },
    background: {
      default: '#FCF5E5',
      paper: '#FFFFFF'
    }
  },
  typography: {
    fontFamily: 'Raleway'
  },
  components: {
    MuiToolbar: {
      styleOverrides: {
        root: {
          height: '50',
          minHeight: '48',
          maxHeight: '50',
        },
        regular: {
          height: '50',
          minHeight: '48',
          maxHeight: '50',
        }
      }
    },
    MuiAlert: {
      styleOverrides: {
        root: ({ ownerState }) => ({
          ...(ownerState.severity === 'info' && {
            backgroundColor: '#60a5fa'
          })
        })
      }
    },
    MuiCssBaseline: {
      styleOverrides: `
                body {
                    margin: 0;
                    padding: 0;
                }           
                
                /* latin */
                @font-face {
                  font-family: 'Open Sans';
                  font-style: normal;
                  font-weight: 300;
                  font-stretch: 100%;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/opensans/v36/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Open Sans';
                  font-style: normal;
                  font-weight: 400;
                  font-stretch: 100%;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/opensans/v36/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Open Sans';
                  font-style: normal;
                  font-weight: 500;
                  font-stretch: 100%;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/opensans/v36/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Open Sans';
                  font-style: normal;
                  font-weight: 700;
                  font-stretch: 100%;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/opensans/v36/memvYaGs126MiZpBA-UvWbX2vVnXBbObj2OVTS-muw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 100;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 300;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 400;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 500;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 700;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Raleway';
                  font-style: normal;
                  font-weight: 900;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/raleway/v29/1Ptug8zYS_SKggPNyC0ITw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Shantell Sans';
                  font-style: italic;
                  font-weight: 800;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/shantellsans/v9/FeUcS0pCoLIo-lcdY7kjvNoQg2xkycTqsuA6bi9pTt8YiT-NXidjb_ee-maigL6R8nKVh8BbE1mv4wwmM0WUkSqmTpG0CADy8v8Ziw.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Shantell Sans';
                  font-style: normal;
                  font-weight: 300;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/shantellsans/v9/FeVvS0pCoLIo-lcdY7kjvNoQqWVWB0qWpl29ajppTuUTu_kJKmHesPOL-maYi4xZeHCNQ09eBlmv8ws8PQ.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Shantell Sans';
                  font-style: normal;
                  font-weight: 400;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/shantellsans/v9/FeVvS0pCoLIo-lcdY7kjvNoQqWVWB0qWpl29ajppTuUTu_kJKmHesPOL-maYi4xZeHCNQ09eBlmv8ws8PQ.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Shantell Sans';
                  font-style: normal;
                  font-weight: 500;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/shantellsans/v9/FeVvS0pCoLIo-lcdY7kjvNoQqWVWB0qWpl29ajppTuUTu_kJKmHesPOL-maYi4xZeHCNQ09eBlmv8ws8PQ.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                
                /* latin */
                @font-face {
                  font-family: 'Shantell Sans';
                  font-style: normal;
                  font-weight: 700;
                  font-display: swap;
                  src: url(https://fonts.gstatic.com/s/shantellsans/v9/FeVvS0pCoLIo-lcdY7kjvNoQqWVWB0qWpl29ajppTuUTu_kJKmHesPOL-maYi4xZeHCNQ09eBlmv8ws8PQ.woff2) format('woff2');
                  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
                }
                            
            `
    }
  }
})

theme = responsiveFontSizes(theme)
theme = createTheme(theme, {
  mixins: {
    toolbar: {
      minHeight: 48,
      maxHeight: 50,
      [theme.breakpoints.up('sm')]: {
        minHeight: 50,
        maxHeight: 50
      }
    }
  }
})

export default theme
