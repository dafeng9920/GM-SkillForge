import React, { useEffect, useRef, useState } from 'react';
import homeStyles from '../../pages/governance/HomePage.module.css';
import type { IntentState } from '../../features/governanceInteraction/interactionDecision';

export interface ComposerAction {
  label: string;
  prompt: string;
  icon?: string;
  intentHint?: IntentState;
}

export interface GovernComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void | Promise<void>;
  placeholder: string;
  submitLabel: string;
  addAttachmentLabel: string;
  imageActionLabel: string;
  fileActionLabel: string;
  enterKeyLabel: string;
  enterLabel: string;
  shiftEnterKeyLabel: string;
  newlineLabel: string;
  separatorLabel: string;
  imageAttachedLabel: string;
  fileAttachedLabel: string;
  quickActions?: ComposerAction[];
  onQuickActionSelect?: (action: ComposerAction) => void;
  selectedIntent?: IntentState;
  intentTabs?: Array<{ key: IntentState; label: string }>;
  onIntentSelect?: (intent: IntentState) => void;
  headerBadge?: string;
  headerText?: string;
  footerHint?: string;
}

export const GovernComposer: React.FC<GovernComposerProps> = ({
  value,
  onChange,
  onSubmit,
  placeholder,
  submitLabel,
  addAttachmentLabel,
  imageActionLabel,
  fileActionLabel,
  enterKeyLabel,
  enterLabel,
  shiftEnterKeyLabel,
  newlineLabel,
  separatorLabel,
  imageAttachedLabel,
  fileAttachedLabel,
  quickActions,
  onQuickActionSelect,
  selectedIntent,
  intentTabs,
  onIntentSelect,
  headerBadge,
  headerText,
  footerHint,
}) => {
  const [attachedImageName, setAttachedImageName] = useState('');
  const [attachedFileName, setAttachedFileName] = useState('');
  const [attachmentMenuOpen, setAttachmentMenuOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const imageInputRef = useRef<HTMLInputElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) {
      return;
    }

    textarea.style.height = '0px';
    const nextHeight = Math.min(Math.max(textarea.scrollHeight, 120), 400);
    textarea.style.height = `${nextHeight}px`;
  }, [value]);

  const handleComposerKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  };

  return (
    <>
      <div className={homeStyles.composer}>
        {(headerBadge || headerText) && (
          <div className={homeStyles.composerPrompt}>
            {headerBadge ? <span className={homeStyles.confirmationBadge}>{headerBadge}</span> : null}
            {headerText ? <p className={homeStyles.composerPromptText}>{headerText}</p> : null}
          </div>
        )}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleComposerKeyDown}
          className={homeStyles.commandInput}
          placeholder={placeholder}
          rows={2}
        />
        <div className={homeStyles.inputDock}>
          <div className={homeStyles.inputDockLeft}>
            <button
              type="button"
              className={homeStyles.plusButton}
              onClick={() => setAttachmentMenuOpen((current) => !current)}
              aria-label={addAttachmentLabel}
            >
              +
            </button>
            {attachmentMenuOpen && (
              <div className={homeStyles.attachmentMenu}>
                <button
                  type="button"
                  className={homeStyles.attachmentMenuItem}
                  onClick={() => {
                    setAttachmentMenuOpen(false);
                    imageInputRef.current?.click();
                  }}
                >
                  {imageActionLabel}
                </button>
                <button
                  type="button"
                  className={homeStyles.attachmentMenuItem}
                  onClick={() => {
                    setAttachmentMenuOpen(false);
                    fileInputRef.current?.click();
                  }}
                >
                  {fileActionLabel}
                </button>
              </div>
            )}
            {intentTabs && onIntentSelect ? (
              <div className={homeStyles.quickRow} style={{ justifyContent: 'flex-start', gap: 10, order: 'unset' }}>
                {intentTabs.map((tab) => (
                  <button
                    key={tab.key}
                    type="button"
                    className={homeStyles.quickAction}
                    style={selectedIntent === tab.key ? { borderColor: 'rgba(234,88,12,0.35)', color: '#fdba74', background: 'rgba(234,88,12,0.08)' } : undefined}
                    onClick={() => onIntentSelect(tab.key)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            ) : null}
          </div>
          <span className={homeStyles.enterHint}>
            <kbd className={homeStyles.kbd}>{enterKeyLabel}</kbd>
            <span>{enterLabel}</span>
            <span className={homeStyles.hintSeparator}>{separatorLabel}</span>
            <kbd className={homeStyles.kbd}>{shiftEnterKeyLabel}</kbd>
            <span>{newlineLabel}</span>
          </span>
          <button type="button" onClick={onSubmit} className={homeStyles.startButton}>
            {submitLabel}
          </button>
        </div>
        <div className={homeStyles.composerFooter}>
          <div className={homeStyles.attachmentSummary}>
            {attachedImageName && (
              <span className={homeStyles.attachmentTag}>
                {imageAttachedLabel}: {attachedImageName}
              </span>
            )}
            {attachedFileName && (
              <span className={homeStyles.attachmentTag}>
                {fileAttachedLabel}: {attachedFileName}
              </span>
            )}
            {footerHint ? <span className={homeStyles.enterHint}>{footerHint}</span> : null}
          </div>
        </div>
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          className={homeStyles.hiddenInput}
          onChange={(event) => setAttachedImageName(event.target.files?.[0]?.name || '')}
        />
        <input
          ref={fileInputRef}
          type="file"
          className={homeStyles.hiddenInput}
          onChange={(event) => setAttachedFileName(event.target.files?.[0]?.name || '')}
        />
      </div>
      {quickActions?.length ? (
        <div className={homeStyles.quickRow}>
          {quickActions.map((action) => (
            <button
              key={action.label}
              type="button"
              className={homeStyles.quickAction}
              onClick={() => onQuickActionSelect?.(action)}
            >
              {action.icon ? <span className={homeStyles.quickActionIcon}>{action.icon}</span> : null}
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </>
  );
};
