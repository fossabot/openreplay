const colors = require('./app/theme/colors');

module.exports = {
	// important: true,
  	content: [
		'./app/**/*.tsx',
		'./app/**/*.js',
  	],
//   corePlugins: [
// 		'preflight',
// 		'container',
// 		// 'accessibility',
// 		// 'alignContent',
// 		'alignItems',
// 		'alignSelf',
// 		//'appearance',
// 		// 'backgroundAttachment',
// 		'backgroundColor',
// 		'backgroundOpacity',
// 		// 'backgroundPosition',
// 		// 'backgroundRepeat',
// 		// 'backgroundSize',
// 		// 'borderCollapse',
// 		'borderColor',
// 		'borderOpacity',
// 		'borderRadius',
// 		// 'borderStyle',
// 		'borderWidth',
// 		// 'boxSizing',
// 		// 'boxShadow',
// 		// 'clear',
// 		'cursor',
// 		'display',
// 		// 'divideColor',
// 		// 'divideWidth',
// 		// 'fill',
// 		'flex',
// 		'flexDirection',
// 		// 'flexGrow',
// 		'flexShrink',
// 		'flexWrap',
// 		// 'float',
// 		'gap',
// 		'gridAutoFlow',
// 		'gridColumn',
// 		'gridColumnStart',
// 		'gridColumnEnd',
// 		'gridRow',
// 		'gridRowStart',
// 		'gridRowEnd',
// 		'gridTemplateColumns',
// 		'gridTemplateRows',
// 		'fontFamily',
// 		'fontSize',
// 		//'fontSmoothing',
// 		'fontStyle',
// 		'fontWeight',
// 		'height',
// 		'inset',
// 		'justifyContent',
// 		'justifySelf',
// 		'letterSpacing',
// 		'lineHeight',
// 		// 'listStylePosition',
// 		// 'listStyleType',
// 		'margin',
// 		// 'maxHeight',
// 		// 'maxWidth',
// 		// 'minHeight',
// 		// 'minWidth',
// 		// 'objectFit',
// 		// 'objectPosition',
// 		'opacity',
// 		// 'order',
// 		'outline',
// 		'overflow',
// 		'padding',
// 		// 'placeholderColor',
// 		// 'placeholderOpacity',
// 		'pointerEvents',
// 		'position',
// 		// 'resize',
// 		// 'rotate',
// 		// 'scale',
// 		// 'skew',
// 		// 'space',
// 		// 'stroke',
// 		// 'strokeWidth',
// 		// 'tableLayout',
// 		'textAlign',
// 		// 'textColor',
// 		// 'textOpacity',
// 		'textDecoration',
// 		'textTransform',
// 		// 'transform',
// 		// 'transitionDuration',
// 		// 'transitionProperty',
// 		// 'transitionTimingFunction',
// 		// 'translate',
// 		'userSelect',
// 		// 'verticalAlign',
// 		'visibility',
// 		'whitespace',
// 		'width',
// 		'wordBreak',
// 		'zIndex'
//   	],
  	theme: {
		colors,
		// borderColor: {
		// 	default: '#DDDDDD',
		// 	"gray-light-shade": colors["gray-light-shade"],
		// 	"blue": colors["active-blue-border"],
		// },
    	extend: {
			boxShadow: {
				'border-blue': `0 0 0 1px ${colors['active-blue-border']}`,
				'border-main': `0 0 0 1px ${colors['main']}`,
				'border-gray': '0 0 0 1px #999',
			},
			keyframes: {
          'fade-in': {
              '0%': {
                  opacity: '0',
                  // transform: 'translateY(-10px)'
              },
              '100%': {
                  opacity: '1',
                  // transform: 'translateY(0)'
              },
          }
      },
      animation: {
          'fade-in': 'fade-in 0.2s ease-out'
      },
      colors: {
        'disabled-text': 'rgba(0,0,0, 0.38)',
      },
      boxShadow: {
        'border-blue': `0 0 0 1px ${colors['active-blue-border']}`,
        'border-main': `0 0 0 1px ${colors['main']}`,
        'border-gray': '0 0 0 1px #999',
      }
		},
  },
  content: [],
  variants: {
		visibility: ['responsive', 'hover', 'focus', 'group-hover']
	},
	plugins: [],
}
