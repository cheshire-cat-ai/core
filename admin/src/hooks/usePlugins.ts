import { type AppDispatch } from '@store/index'
import { selectAllPlugins, selectPluginsError, selectPluginsIsLoading } from '@store/plugins/selectors'
import { fetchPluginsModels } from '@store/plugins/slice'
import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'

/**
 * A custom hook that returns the Plugins state
 */
const usePlugins = () => {
  const plugins = useSelector(selectAllPlugins)
  const isLoading = useSelector(selectPluginsIsLoading)
  const error = useSelector(selectPluginsError)
  const dispatch = useDispatch<AppDispatch>()

  const requirePlugins = useCallback(() => {
    return dispatch(fetchPluginsModels())
  }, [dispatch])

  return {
    plugins,
    isLoading,
    error,
    requirePlugins
  }
}

export default usePlugins
