// ROI Calculator Integration with Pipedream
// This script connects the ROI calculator form to the Pipedream webhook

const WEBHOOK_URL = 'https://eo3knqie30y3fhp.m.pipedream.net';

// Function to collect form data
function collectROIFormData() {
    const formData = {};
    
    // Basic contact information
    const nameField = document.querySelector('#name, [name="name"], .name-field');
    const emailField = document.querySelector('#email, [name="email"], .email-field');
    const companyField = document.querySelector('#company, [name="company"], .company-field');
    const phoneField = document.querySelector('#phone, [name="phone"], .phone-field');
    
    if (nameField) formData.name = nameField.value;
    if (emailField) formData.email = emailField.value;
    if (companyField) formData.company = companyField.value;
    if (phoneField) formData.phone = phoneField.value;
    
    // ROI Calculator specific fields
    const revenueField = document.querySelector('#revenue, [name="revenue"], .revenue-field');
    const budgetField = document.querySelector('#budget, [name="budget"], .budget-field');
    const employeesField = document.querySelector('#employees, [name="employees"], .employees-field');
    const industryField = document.querySelector('#industry, [name="industry"], .industry-field');
    const goalsField = document.querySelector('#goals, [name="goals"], .goals-field');
    
    if (revenueField) formData.currentRevenue = revenueField.value;
    if (budgetField) formData.marketingBudget = budgetField.value;
    if (employeesField) formData.employeeCount = employeesField.value;
    if (industryField) formData.industry = industryField.value;
    if (goalsField) formData.businessGoals = goalsField.value;
    
    // Add timestamp and source
    formData.timestamp = new Date().toISOString();
    formData.source = 'hireyourcmo.ai';
    formData.calculatorType = 'ROI';
    
    return formData;
}

// Function to display ROI results
function displayROIResults(analysisData) {
    const resultsContainer = document.querySelector('#roi-results, .roi-results, .results-container');
    
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }
    
    const analysis = analysisData.roi_analysis;
    
    const resultsHTML = `
        <div class="roi-analysis-results">
            <h3>תוצאות ניתוח ROI מותאמות אישית</h3>
            
            <div class="executive-summary">
                <h4>סיכום מנהלים</h4>
                <p>${analysis.executive_summary}</p>
            </div>
            
            <div class="roi-metrics">
                <h4>מדדי ROI</h4>
                <ul>
                    <li>אחוז ROI משוער: ${analysis.roi_metrics.estimated_roi_percentage}%</li>
                    <li>תקופת החזר: ${analysis.roi_metrics.payback_period_years} שנים</li>
                    <li>NPV: $${analysis.roi_metrics.npv}</li>
                </ul>
            </div>
            
            <div class="recommendations">
                <h4>המלצות</h4>
                <ul>
                    ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
            
            <div class="risk-assessment">
                <h4>הערכת סיכונים</h4>
                <div class="risks">
                    <h5>סיכונים פוטנציאליים:</h5>
                    <ul>
                        ${analysis.risk_assessment.potential_risks.map(risk => `<li>${risk}</li>`).join('')}
                    </ul>
                </div>
                <div class="mitigation">
                    <h5>אסטרטגיות הפחתת סיכונים:</h5>
                    <ul>
                        ${analysis.risk_assessment.mitigation_strategies.map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="timeline">
                <h4>לוח זמנים ליישום</h4>
                <ul>
                    <li>השקעה ראשונית: ${analysis.timeline.initial_investment}</li>
                    <li>השקת קמפיין שיווקי: ${analysis.timeline.marketing_campaign_launch}</li>
                    <li>אופטימיזציה של שרשרת האספקה: ${analysis.timeline.supply_chain_optimization}</li>
                    <li>השלמת שדרוג טכנולוגי: ${analysis.timeline.technology_upgrade_completion}</li>
                    <li>מימוש ROI צפוי: ${analysis.timeline.expected_roi_realization}</li>
                </ul>
            </div>
            
            <div class="financial-projections">
                <h4>תחזיות פיננסיות</h4>
                <p>עלות השקעה ראשונית: $${analysis.financial_projections.initial_investment_cost}</p>
                <p>הכנסות שנתיות צפויות: ${analysis.financial_projections.projected_annual_revenue.join(', ')}</p>
                <p>חיסכון שנתי צפוי: ${analysis.financial_projections.projected_annual_savings.join(', ')}</p>
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = resultsHTML;
    resultsContainer.style.display = 'block';
}

// Function to show loading state
function showLoading() {
    const resultsContainer = document.querySelector('#roi-results, .roi-results, .results-container');
    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="loading">מעבד את הנתונים שלך עם AI... אנא המתן</div>';
        resultsContainer.style.display = 'block';
    }
}

// Function to show error
function showError(message) {
    const resultsContainer = document.querySelector('#roi-results, .roi-results, .results-container');
    if (resultsContainer) {
        resultsContainer.innerHTML = `<div class="error">שגיאה: ${message}</div>`;
        resultsContainer.style.display = 'block';
    }
}

// Main function to handle form submission
async function handleROIFormSubmission(event) {
    if (event) {
        event.preventDefault();
    }
    
    try {
        showLoading();
        
        // Collect form data
        const formData = collectROIFormData();
        
        console.log('Sending data to Pipedream:', formData);
        
        // Send to Pipedream webhook
        const response = await fetch(WEBHOOK_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Received analysis:', result);
        
        // Display results
        displayROIResults(result);
        
    } catch (error) {
        console.error('Error processing ROI calculation:', error);
        showError('אירעה שגיאה בעיבוד הנתונים. אנא נסה שוב.');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Find the ROI form
    const roiForm = document.querySelector('#roi-form, .roi-form, form[data-roi], form.calculator-form');
    
    if (roiForm) {
        roiForm.addEventListener('submit', handleROIFormSubmission);
        console.log('ROI Calculator integration initialized');
    } else {
        console.warn('ROI form not found. Looking for submit button...');
        
        // Alternative: look for submit button
        const submitButton = document.querySelector('#calculate-roi, .calculate-roi, [data-calculate], .submit-btn');
        if (submitButton) {
            submitButton.addEventListener('click', handleROIFormSubmission);
            console.log('ROI Calculator integration initialized via button');
        } else {
            console.error('Could not find ROI form or submit button');
        }
    }
});

// Export for manual use
window.calculateROI = handleROIFormSubmission;
window.roiIntegration = {
    collectData: collectROIFormData,
    displayResults: displayROIResults,
    calculate: handleROIFormSubmission
};