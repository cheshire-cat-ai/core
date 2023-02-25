/**
 * This module defines and exports all the question-related services.
 */

/**
 * Fetches the most frequently asked questions from the API.
 */
export const fetchMostFrequentlyAskedQuestions = async () => {
  return await Promise.resolve([
    'What\'s up?',
    'Who\'s the Queen of Hearts?',
    'Where is the white rabbit?',
    'What is Python?',
    'How do I write my own AI app?',
    'Does pineapple belong on pizza?'
  ])
}
