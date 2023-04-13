/**
 * This file defines and exports animation objects for Framer Motion.
 * These objects can be used to animate any Framer Motion component
 */

export const fadeInOut = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.25, easing: [0.42, 0, 0.58, 1] }
}

export const slideLeftInOut = {
  initial: { translateX: '-100%' },
  animate: { translateX: 0 },
  exit: { translateX: '-100%' },
  transition: { duration: 0.4, easing: [0.42, 0, 0.58, 1] }
}

export const slideRightInOUt = {
  initial: { translateX: '100%' },
  animate: { translateX: 0 },
  exit: { translateX: '100%' },
  transition: { duration: 0.3, easing: [0.42, 0, 0.58, 1] }
}

export const slideBottomInOUt = {
  initial: { opacity: 0, translateY: 100 },
  animate: { opacity: 1, translateY: 0 },
  exit: { opacity: 0, translateY: -10 },
  transition: { duration: 0.5, easing: [0.6, -0.05, 0.01, 0.99], delay: 0.15 }
}
