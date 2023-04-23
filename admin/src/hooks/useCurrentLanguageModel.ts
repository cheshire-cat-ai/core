import { useDispatch, useSelector } from 'react-redux'
import { type AppDispatch } from '@store/index'
import {
  selectCurrentLanguageModel,
  selectCurrentLanguageModelSettings,
  selectLanguageModelsUpdating
} from '@store/languageModels/selector'
import { useCallback } from 'react'
import { setLLMSettings, updateLanguageModelSettings } from '@store/languageModels/slice'
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'

const useCurrentLanguageModel = () => {
  const dispatch = useDispatch<AppDispatch>()
  const updating = useSelector(selectLanguageModelsUpdating)
  const selected = useSelector(selectCurrentLanguageModel)
  const settings = useSelector(selectCurrentLanguageModelSettings)

  const updateProviderSettings = useCallback(() => {
    if (settings && selected) {
      return dispatch(updateLanguageModelSettings({ name: selected, settings }))
    }
  }, [dispatch, selected, settings])

  const setCurrentProviderSettings = useCallback((nextSettings: SettingsRecord) => {
    if (nextSettings && selected) {
      return dispatch(setLLMSettings({ name: selected, settings: nextSettings }))
    }
  }, [dispatch, selected])

  return {
    updating,
    selected,
    settings,
    updateProviderSettings,
    setCurrentProviderSettings
  }
}

export default useCurrentLanguageModel
