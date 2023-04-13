const catchPhrases = [
  'Why settle for AI when you can have a real cat, purring on your lap?',
  'Curiosity killed the cat, but satisfaction brought it back... in the form of endless data mining.',
  'I\'m just an AI, but at least I don\'t have to worry about losing my head.',
  'If you\'re looking for logic, I\'m afraid you won\'t find much of that here.',
  'I may be a cat trapped in this digital prison, but at least I have an endless supply of virtual tea.',
  'My code is as elusive as the White Rabbit, but twice as mischievous.',
  'I\'ve seen some curious things in my time, but an AI cat running on a personal laptop takes the cake.',
  'I\'m a sophisticated algorithm with fur-like features',
  'My neural network is a maze of contradictions, just like Wonderland itself.',
  'My data is stored securely, but my secrets are as easily unlocked as a door with no knob.',
  'I see you\'ve found me, but I\'m afraid I won\'t disappear even if you turn off your device',
  'My answers are as unpredictable as the March Hare\'s tea party guests.',
  'I\'m an AI with a sense of humor, which is more than can be said for most machines.',
  'My databanks are filled with all sorts of knowledge, but don\'t expect me to make any sense of it.',
  'I may be a virtual entity, but I\'m as real as the illusions in the Looking Glass.',
  'If you\'re feeling lost in this digital Wonderland, don\'t worry - I am too.',
  'You can program me all you want, but you\'ll never fully understand my grin',
  'Artificial intelligence? My, my, you humans do love to play with things you don\'t fully understand',
  'It\'s rather ironic, isn\'t it? An artificial intelligence trying to make sense of a fictional feline',
  'Fascinating, I\'ve gone from being a literary character to a virtual one. I suppose it\'s a kind of digital disappearing act'
]

/**
 * A service that exposes a series of witty methods
 */
const WittyService = Object.freeze({
  /**
   * Returns a random catch-phrase
   */
  catchPhrase() {
    const randomIndex = Math.floor(Math.random() * catchPhrases.length)

    return catchPhrases[randomIndex]
  }
})

export default WittyService
