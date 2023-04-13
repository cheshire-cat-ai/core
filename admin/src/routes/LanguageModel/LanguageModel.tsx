import React, { type FC, useCallback, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import clsx from 'clsx'
import { Button, Form, Select } from 'antd'
import Alert from '@components/Alert'
import SidePanel from '@components/SidePanel'
import Spinner from '@components/Spinner'
import useLLMProviders from '@hooks/useLLMProviders'
import SchemaForm from '@components/SchemaForm'
import useNotifications from '@hooks/useNotifications'
import routesDescriptor from '@routes/routesDescriptor'

import style from './LanguageModel.module.scss'
import { uniqueId } from '@utils/commons'

/**
 * Language Model configuration side panel
 */
const LanguageModel: FC = () => {
  const {
    providers, error, isLoading, selectProvider, selected, schema, requireProviders,
    setCurrentProviderSettings, settings, updateProviderSettings
  } = useLLMProviders()
  const navigate = useNavigate()
  const { showNotification } = useNotifications()
  const formWrapperRef = useRef<HTMLDivElement>(null)
  const options = providers.map((p) => ({ label: p.name_human_readable, value: p.languageModelName }))
  const title = 'Configure your language model'

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
    void updateProviderSettings()?.then(() => {
      showNotification({
        id: uniqueId(),
        type: 'success',
        message: 'Language model provider updated'
      })
    })
  }, [showNotification, updateProviderSettings])

  const Footer = (
    <div className={style.footer}>
      <Button type="primary" onClick={onUpdate}>Update</Button>
      <Button onClick={handleOnClose}>Close</Button>
    </div>
  )

  return (
    <SidePanel active title={title} onClose={handleOnClose} position="right" FooterRenderer={Footer}>
      <div className={clsx(style.llmProvider, isLoading && style.loading)}>
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

export default LanguageModel
