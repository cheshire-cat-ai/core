/**
 * Create initial state for an async data state
 */
export const createAsyncInitialState = <TState = any>(initialData: TState) => {
  return {
    data: initialData,
    loading: false,
    error: null
  }
}
