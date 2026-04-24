-- FinSight AI: Supabase Database Schema

-- 1. Enums
CREATE TYPE financial_literacy_level AS ENUM ('beginner', 'intermediate', 'expert');
CREATE TYPE risk_profile AS ENUM ('Conservative', 'Moderate', 'Aggressive');
CREATE TYPE message_role AS ENUM ('user', 'assistant');

-- 2. Tables

-- Profiles: Extension of auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT,
    financial_literacy_level financial_literacy_level DEFAULT 'beginner',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Risk Assessments: Results from ML pipeline
CREATE TABLE IF NOT EXISTS public.risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    age_range TEXT NOT NULL,
    income_range TEXT NOT NULL,
    self_reported_tolerance TEXT CHECK (self_reported_tolerance IN ('Low', 'Medium', 'High')),
    investment_horizon_years INTEGER,
    primary_goal TEXT,
    has_dependents BOOLEAN DEFAULT FALSE,
    savings_level TEXT,
    debt_level TEXT,
    predicted_risk_profile risk_profile,
    confidence_score FLOAT,
    shap_values JSONB,
    top_features JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fund Recommendations: AI-generated suggestions based on assessment
CREATE TABLE IF NOT EXISTS public.fund_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES public.risk_assessments(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    fund_name TEXT NOT NULL,
    fund_type TEXT NOT NULL,
    narrative TEXT,
    rationale_points JSONB,
    suitability_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Sessions: Container for AI conversations
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    assessment_id UUID REFERENCES public.risk_assessments(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages: Individual messages within a session
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE NOT NULL,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs: System-wide activity tracking
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    metadata JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fairness Reports: Bias detection metrics for ML assessments
CREATE TABLE IF NOT EXISTS public.fairness_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID REFERENCES public.risk_assessments(id) ON DELETE CASCADE NOT NULL,
    age_bias_score FLOAT,
    income_bias_score FLOAT,
    gender_bias_score FLOAT,
    overall_fairness_score FLOAT,
    flags JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Row Level Security (RLS)

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fund_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fairness_reports ENABLE ROW LEVEL SECURITY;

-- Policies for standard tables (User access)
CREATE POLICY "Users can manage their own profile" ON public.profiles
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can view their own assessments" ON public.risk_assessments
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view their own recommendations" ON public.fund_recommendations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own chat sessions" ON public.chat_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own chat messages" ON public.chat_messages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.chat_sessions
            WHERE id = chat_messages.session_id AND user_id = auth.uid()
        )
    );

-- Policies for restricted tables (Audit & Fairness)
CREATE POLICY "Users can insert audit logs" ON public.audit_logs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Service role can select audit logs" ON public.audit_logs
    FOR SELECT USING (auth.role() = 'service_role');

CREATE POLICY "Users can insert fairness reports" ON public.fairness_reports
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Service role can select fairness reports" ON public.fairness_reports
    FOR SELECT USING (auth.role() = 'service_role');

-- 4. Triggers & Functions

-- Automatically create a profile when a new user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name)
    VALUES (new.id, new.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Updated_at trigger for profiles
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_profile_updated
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- 5. Indexes
CREATE INDEX idx_profiles_user_id ON public.profiles(id);
CREATE INDEX idx_risk_assessments_user_id ON public.risk_assessments(user_id);
CREATE INDEX idx_risk_assessments_created_at ON public.risk_assessments(created_at);
CREATE INDEX idx_risk_assessments_profile ON public.risk_assessments(predicted_risk_profile);
CREATE INDEX idx_fund_recommendations_user_id ON public.fund_recommendations(user_id);
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_fairness_reports_assessment_id ON public.fairness_reports(assessment_id);
