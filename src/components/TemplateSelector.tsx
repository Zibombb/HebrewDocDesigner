import React from 'react';
import { LetterTemplate, LetterCategory } from '../types/patient';
import { letterTemplates, categoryLabels } from '../templates/letterTemplates';
import './TemplateSelector.css';

interface TemplateSelectorProps {
  selectedTemplate: LetterTemplate | null;
  onSelect: (template: LetterTemplate) => void;
}

export const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  selectedTemplate,
  onSelect
}) => {
  const [activeCategory, setActiveCategory] = React.useState<LetterCategory | 'all'>('all');

  const categories: (LetterCategory | 'all')[] = ['all', 'referral', 'summary', 'certificate', 'prescription', 'general'];

  const filteredTemplates = activeCategory === 'all'
    ? letterTemplates
    : letterTemplates.filter(t => t.category === activeCategory);

  const getCategoryIcon = (category: string): string => {
    const icons: Record<string, string> = {
      all: '📋',
      referral: '📤',
      summary: '📝',
      certificate: '📜',
      prescription: '💊',
      general: '📄'
    };
    return icons[category] || '📄';
  };

  return (
    <div className="template-selector">
      <h3 className="form-section-title">בחירת תבנית מכתב</h3>

      <div className="category-tabs">
        {categories.map(category => (
          <button
            key={category}
            className={`category-tab ${activeCategory === category ? 'active' : ''}`}
            onClick={() => setActiveCategory(category)}
          >
            <span className="category-icon">{getCategoryIcon(category)}</span>
            <span className="category-label">
              {category === 'all' ? 'הכל' : categoryLabels[category]}
            </span>
          </button>
        ))}
      </div>

      <div className="templates-grid">
        {filteredTemplates.map(template => (
          <div
            key={template.id}
            className={`template-card ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
            onClick={() => onSelect(template)}
          >
            <div className="template-icon">{getCategoryIcon(template.category)}</div>
            <div className="template-info">
              <h4 className="template-name">{template.nameHebrew}</h4>
              <p className="template-description">{template.description}</p>
            </div>
            {selectedTemplate?.id === template.id && (
              <div className="selected-indicator">✓</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
