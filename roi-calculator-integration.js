// ROI Calculator Integration with Pipedream Webhook
// This script integrates the existing marketing effectiveness quiz with OpenAI analysis

(function() {
    'use strict';
    
    // Configuration
    const WEBHOOK_URL = 'https://eo3knqie30y3fhp.m.pipedream.net';
    
    // Store quiz answers
    let quizAnswers = {};
    let currentQuestion = 0;
    
    // Question mapping for the 5 marketing effectiveness questions
    const questionKeys = [
        'automationLevel',
        'timeWaster', 
        'dataTracking',
        'leadGeneration',
        'marketingROI'
    ];
    
    // Override the existing selectAnswer function
    const originalSelectAnswer = window.selectAnswer;
    window.selectAnswer = function(questionIndex, answerValue, answerText) {
        // Call original function to maintain existing UI behavior
        if (originalSelectAnswer) {
            originalSelectAnswer(questionIndex, answerValue, answerText);
        }
        
        // Store the answer
        const questionKey = questionKeys[questionIndex];
        if (questionKey) {
            quizAnswers[questionKey] = {
                value: answerValue,
                text: answerText,
                questionIndex: questionIndex
            };
        }
        
        console.log('Answer stored:', questionKey, answerValue, answerText);
        
        // Check if this is the last question
        if (questionIndex === questionKeys.length - 1) {
            // Small delay to ensure UI updates, then send to webhook
            setTimeout(() => {
                sendQuizDataToWebhook();
            }, 500);
        }
    };
    
    // Function to send quiz data to Pipedream webhook
    async function sendQuizDataToWebhook() {
        try {
            console.log('Sending quiz data to webhook:', quizAnswers);
            
            // Prepare the payload
            const payload = {
                quizType: 'marketing_effectiveness',
                answers: quizAnswers,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                referrer: document.referrer,
                url: window.location.href
            };
            
            // Show loading state
            showLoadingState();
            
            // Send to webhook
            const response = await fetch(WEBHOOK_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Webhook response:', result);
            
            // Display the real AI analysis results
            displayResults(result);
            
        } catch (error) {
            console.error('Error sending quiz data:', error);
            // Show fallback results if webhook fails
            displayFallbackResults();
        }
    }
    
    // Function to show loading state
    function showLoadingState() {
        const resultsContainer = document.getElementById('quiz-results') || 
                               document.querySelector('.quiz-results') ||
                               document.querySelector('#results');
        
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="loading-container" style="text-align: center; padding: 20px;">
                    <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto 20px;"></div>
                    <h3>מנתח את התשובות שלך...</h3>
                    <p>אנא המתן בזמן שאנו מכינים עבורך ניתוח מותאם אישית</p>
                </div>
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;
        }
    }
    
    // Function to display real AI analysis results
    function displayResults(data) {
        const resultsContainer = document.getElementById('quiz-results') || 
                               document.querySelector('.quiz-results') ||
                               document.querySelector('#results');
        
        if (!resultsContainer) {
            console.error('Results container not found');
            return;
        }
        
        const { quiz_results, analysis, next_steps } = data;
        
        resultsContainer.innerHTML = `
            <div class="ai-results" style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                <div class="score-section" style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
                    <h2 style="margin: 0 0 10px 0;">הציון שלך</h2>
                    <div class="score-display" style="font-size: 48px; font-weight: bold; margin: 10px 0;">${quiz_results.score}/${quiz_results.max_score}</div>
                    <div class="percentage" style="font-size: 24px; margin: 5px 0;">${quiz_results.percentage}%</div>
                    <div class="performance-level" style="font-size: 18px; background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; display: inline-block;">${quiz_results.performance_level}</div>
                </div>
                
                <div class="analysis-section" style="margin-bottom: 25px;">
                    <h3 style="color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">ניתוח התוצאות</h3>
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">${analysis.summary}</p>
                </div>
                
                <div class="strengths-section" style="margin-bottom: 25px;">
                    <h3 style="color: #27ae60; border-bottom: 2px solid #27ae60; padding-bottom: 10px;">הנקודות החזקות שלך</h3>
                    <ul style="list-style: none; padding: 0;">
                        ${analysis.strengths.map(strength => `<li style="padding: 8px 0; border-left: 4px solid #27ae60; padding-left: 15px; margin: 10px 0; background: #f8f9fa;">✓ ${strength}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="opportunities-section" style="margin-bottom: 25px;">
                    <h3 style="color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">הזדמנויות לשיפור</h3>
                    <ul style="list-style: none; padding: 0;">
                        ${analysis.opportunities.map(opportunity => `<li style="padding: 8px 0; border-left: 4px solid #e74c3c; padding-left: 15px; margin: 10px 0; background: #f8f9fa;">→ ${opportunity}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="next-steps-section" style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: #333; margin-bottom: 15px;">הצעד הבא</h3>
                    <p style="font-size: 16px; color: #555; margin-bottom: 20px;">${next_steps.message}</p>
                    <p style="font-size: 14px; color: #666; margin-bottom: 20px;">${next_steps.call_to_action}</p>
                    ${next_steps.contact_email ? `<a href="mailto:${next_steps.contact_email}" style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 5px; font-weight: bold;">צור קשר במייל</a>` : ''}
                    ${next_steps.contact_phone ? `<a href="tel:${next_steps.contact_phone}" style="display: inline-block; background: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 5px; font-weight: bold;">התקשר עכשיו</a>` : ''}
                </div>
            </div>
        `;
    }
    
    // Fallback function if webhook fails
    function displayFallbackResults() {
        const resultsContainer = document.getElementById('quiz-results') || 
                               document.querySelector('.quiz-results') ||
                               document.querySelector('#results');
        
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="fallback-results" style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    <h3 style="color: #e74c3c;">שגיאה זמנית</h3>
                    <p>מצטערים, אירעה שגיאה בעת ניתוח התשובות. אנא נסה שוב מאוחר יותר או צור איתנו קשר ישירות.</p>
                    <p><strong>לקבלת ניתוח מותאם אישית, צור קשר:</strong></p>
                    <a href="mailto:shani@shani.marketing" style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px;">shani@shani.marketing</a>
                </div>
            `;
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('ROI Calculator Integration loaded');
        });
    } else {
        console.log('ROI Calculator Integration loaded');
    }
    
})();