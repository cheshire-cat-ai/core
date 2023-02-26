/**
 * This module defines and exports all the question-related services.
 * A service is a function that returns a Promise resolving the API response
 */
/**
 * Fetches the most frequently asked questions from the API.
 *
 * Please note: for the moment this is a mock function that returns a Promise that resolves to a static array of questions.
 */
export const fetchFAQs = async () => {
  return await Promise.resolve([
    'What\'s up?',
    'Who\'s the Queen of Hearts?',
    'Where is the white rabbit?',
    'What is Python?',
    'How do I write my own AI app?',
    'Does pineapple belong on pizza?'
  ])
}
