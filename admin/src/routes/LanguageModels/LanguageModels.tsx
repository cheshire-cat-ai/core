import React, { type FC, useCallback, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import clsx from 'clsx'
import { Button, Form, Select } from 'antd'
import Alert from '@components/Alert'
import SidePanel from '@components/SidePanel'
import Spinner from '@components/Spinner'
import useLanguageModels from '@hooks/useLanguageModels'
import SchemaForm from '@components/SchemaForm'
import useNotifications from '@hooks/useNotifications'
import useCurrentLanguageModel from '@hooks/useCurrentLanguageModel'
import routesDescriptor from '@routes/routesDescriptor'

import style from './LanguageModels.module.scss'

/**
 * Language Model configuration side panel
 */
const LanguageModels: FC = () => {
  const { providers, error, isLoading, selectProvider, schema, requireProviders } = useLanguageModels()
  const { selected, updating, setCurrentProviderSettings, settings, updateProviderSettings } = useCurrentLanguageModel()
  const { showNotification } = useNotifications()
  const navigate = useNavigate()
  const formWrapperRef = useRef<HTMLDivElement>(null)
  const options = providers.map((p) => ({ label: p.name_human_readable, value: p.languageModelName }))

  useEffect(() => {
    void requireProviders()
  }, [requireProviders])

  const handleOnClose = useCallback(() => {
    navigate(routesDescriptor.settings.path)
  }, [navigate])

  const onUpdate = useCallback(() => {
    const button = formWrapperRef.current?.querySelector<HTMLButtonElement>('button[type="submit"]')
    if (button) {
      button.click()
    }
  }, [])

  const onSubmit = useCallback(() => {
    const promise = updateProviderSettings()

    if (promise) {
      void promise
        .then(() => {
          showNotification({
            type: 'success',
            message: 'Language model provider updated'
          })
        })
    }
  }, [showNotification, updateProviderSettings])

  const Footer = (
    <div className={style.footer}>
      <Button type="primary" disabled={updating} onClick={onUpdate}>{updating ? 'Updating...' : 'Update'}</Button>
      <Button onClick={handleOnClose}>Close</Button>
    </div>
  )

  return (
    <SidePanel active title="Configure your language model" onClose={handleOnClose} position="right" FooterRenderer={Footer}>
      <div className={clsx(style.llm, isLoading && style.loading)}>
        {isLoading && <Spinner />}
        {error && <Alert variant="error">{error}</Alert>}
        {!isLoading && !error && providers && (
          <Form name="llm" layout="vertical">
            <Form.Item label="Language Model Provider" name="provider" tooltip="Select your language model provider">
              <Select
                value={selected}
                defaultValue={selected}
                placeholder="Please select your language model provider"
                onChange={selectProvider}
                options={options}
              />
            </Form.Item>
          </Form>
        )}
        {selected && schema && (
          <div ref={formWrapperRef}>
            <SchemaForm
              data={settings}
              onChange={setCurrentProviderSettings}
              onSubmit={onSubmit}
              schema={schema}
              className={style.form}
            />
          </div>
        )}
      </div>
    </SidePanel>
  )
}

export default LanguageModels
