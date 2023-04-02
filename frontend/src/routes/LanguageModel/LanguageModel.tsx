import React, { type FC, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { type RJSFSchema } from '@rjsf/utils'
import clsx from 'clsx'
import { Button, Form, Select } from 'antd'
import Alert from '@components/Alert'
import SidePanel from '@components/SidePanel'
import Spinner from '@components/Spinner'
import useLLMProviders from '@hooks/useLLMProviders'
import { type LLMProviderDescriptor } from '@models/LLMProviderDescriptor'
import SchemaForm from '@components/SchemaForm'

import style from './LanguageModel.module.scss'

const schema: RJSFSchema = {
  type: 'object',
  required: ['key', 'foo'],
  properties: {
    key: { type: 'string', title: 'OpenAI key' },
    something: { type: 'number', title: 'Something else' },
    foo: {
      type: 'object',
      title: 'Nested',
      oneOf: [
        {
          properties: {
            ipsum: {
              type: 'string'
            }
          },
          required: ['ipsum']
        },
        {
          properties: {
            lorem: {
              type: 'string'
            }
          },
          required: ['lorem']
        }
      ]
    }
  }
}

/**
 * Language Model configuration side panel
 */
const LanguageModel: FC = () => {
  const { providers, error, isLoading, selectLLMProvider, selected, requireLLMProviders } = useLLMProviders()
  const navigate = useNavigate()
  const title = 'Configure your language model'

  useEffect(() => {
    void requireLLMProviders()
  }, [requireLLMProviders])

  const handleOnClose = useCallback(() => {
    navigate('/configurations')
  }, [navigate])

  const Footer = (
    <>
      <Button type="primary">Submit</Button>
      <Button type="default">Cancel</Button>
    </>
  )

  return (
    <SidePanel active title={title} onClose={handleOnClose} FooterRenderer={Footer} position="right">
      <div className={clsx(style.llmProvider, isLoading && style.loading)}>
        {isLoading && <Spinner />}
        {error && <Alert variant="error">{error}</Alert>}
        {providers && (
          <Form name="llm" layout="vertical">
            <Form.Item label="Language Model Provider" name="provider" tooltip="Select your language model provider">
              <Select
                value={selected}
                defaultValue={selected}
                placeholder="Please select your language model provider"
                onChange={(val) => selectLLMProvider(val)}
                options={providers.map(toSelectOption)}
              />
            </Form.Item>
          </Form>
        )}
        {selected && (<SchemaForm schema={schema} onChange={console.log} />)}
      </div>
    </SidePanel>
  )
}

const toSelectOption = ({ name, id }: LLMProviderDescriptor) => ({ value: id, label: name })

export default LanguageModel
