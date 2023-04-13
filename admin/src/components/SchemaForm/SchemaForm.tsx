import React, { type FC, useCallback } from 'react'
import clsx from 'clsx'
import validator from '@rjsf/validator-ajv8'
import { type FormProps, type IChangeEvent } from '@rjsf/core'
import Form from '@rjsf/antd'
import { type JSONSchema } from '@models/JSONSchema'
import { type CommonProps } from '@models/commons'

import style from './SchemaForm.module.scss'

/**
 * TODO: document this
 */
const SchemaForm: FC<SchemaFormProps> = ({ data, onChange, schema, className, ...props }) => {
  const classList = clsx(style.form, className)

  const handleChange = useCallback((data: IChangeEvent) => {
    if (onChange) {
      onChange(data.formData)
    }
  }, [onChange])

  return (
    <Form
      schema={schema}
      validator={validator}
      formData={data}
      onChange={handleChange}
      className={classList}
      {...props}
    />
  )
}

export interface SchemaFormProps<TData = any> extends Omit<FormProps, 'className' | 'formData' | 'onChange' | 'validator'>, CommonProps {
  schema: JSONSchema
  data?: TData
  onChange?: (data: TData) => void
}

export default SchemaForm
