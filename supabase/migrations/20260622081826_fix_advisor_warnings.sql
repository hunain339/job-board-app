-- ============================================================
-- FIX 1: SECURITY — rls_policy_always_true (4 policies)
-- Add proper USING clauses to UPDATE policies that have USING(true)
-- ============================================================

-- 1a. applications_application.allow_candidate_update
DROP POLICY IF EXISTS allow_candidate_update ON public.applications_application;
CREATE POLICY allow_candidate_update ON public.applications_application
  FOR UPDATE
  USING ((select auth.uid()) = candidate_id)
  WITH CHECK ((select auth.uid()) = candidate_id);

-- 1b. jobs_job.allow_employer_update
DROP POLICY IF EXISTS allow_employer_update ON public.jobs_job;
CREATE POLICY allow_employer_update ON public.jobs_job
  FOR UPDATE
  USING ((select auth.uid()) = employer_id)
  WITH CHECK ((select auth.uid()) = employer_id);

-- 1c. users_user.allow_user_update_self
DROP POLICY IF EXISTS allow_user_update_self ON public.users_user;
CREATE POLICY allow_user_update_self ON public.users_user
  FOR UPDATE
  USING ((select auth.uid()) = id)
  WITH CHECK ((select auth.uid()) = id);

-- 1d. users_userprofile.allow_user_update_self
DROP POLICY IF EXISTS allow_user_update_self ON public.users_userprofile;
CREATE POLICY allow_user_update_self ON public.users_userprofile
  FOR UPDATE
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);

-- ============================================================
-- FIX 2: PERFORMANCE — auth_rls_initplan (24 policies)
-- Wrap auth.uid() / auth.role() / auth.jwt() in (select ...)
-- ============================================================

-- 2a/2b: applications_application read policies (also merges multiple permissive policies)
DROP POLICY IF EXISTS allow_candidate_read ON public.applications_application;
DROP POLICY IF EXISTS allow_employer_read ON public.applications_application;
CREATE POLICY allow_application_read ON public.applications_application
  FOR SELECT
  USING (
    candidate_id = (select auth.uid())
    OR
    (SELECT jobs_job.employer_id FROM jobs_job WHERE jobs_job.id = applications_application.job_id)::text = (select auth.uid())::text
  );

-- 2c. applications_application.allow_candidate_insert
DROP POLICY IF EXISTS allow_candidate_insert ON public.applications_application;
CREATE POLICY allow_candidate_insert ON public.applications_application
  FOR INSERT
  WITH CHECK (candidate_id = (select auth.uid()));

-- 2d. applications_applicationnote.allow_owner_read
DROP POLICY IF EXISTS allow_owner_read ON public.applications_applicationnote;
CREATE POLICY allow_owner_read ON public.applications_applicationnote
  FOR SELECT
  USING (
    ((SELECT applications_application.candidate_id
      FROM applications_application
      WHERE applications_application.id = applications_applicationnote.application_id)::text = (select auth.uid())::text)
    OR
    ((SELECT (SELECT jobs_job.employer_id FROM jobs_job WHERE jobs_job.id = applications_application.job_id) AS employer_id
      FROM applications_application
      WHERE applications_application.id = applications_applicationnote.application_id)::text = (select auth.uid())::text)
  );

-- 2e. applications_applicationnote.allow_owner_insert
DROP POLICY IF EXISTS allow_owner_insert ON public.applications_applicationnote;
CREATE POLICY allow_owner_insert ON public.applications_applicationnote
  FOR INSERT
  WITH CHECK (employer_id = (select auth.uid()));

-- 2f. applications_applicationstatushistory.allow_owner_read
DROP POLICY IF EXISTS allow_owner_read ON public.applications_applicationstatushistory;
CREATE POLICY allow_owner_read ON public.applications_applicationstatushistory
  FOR SELECT
  USING (
    ((SELECT applications_application.candidate_id
      FROM applications_application
      WHERE applications_application.id = applications_applicationstatushistory.application_id)::text = (select auth.uid())::text)
    OR
    ((SELECT (SELECT jobs_job.employer_id FROM jobs_job WHERE jobs_job.id = applications_application.job_id) AS employer_id
      FROM applications_application
      WHERE applications_application.id = applications_applicationstatushistory.application_id)::text = (select auth.uid())::text)
  );

-- 2g. jobs_job.allow_employer_delete
DROP POLICY IF EXISTS allow_employer_delete ON public.jobs_job;
CREATE POLICY allow_employer_delete ON public.jobs_job
  FOR DELETE
  USING (employer_id = (select auth.uid()));

-- 2h. jobs_jobsavedbyuser.allow_user_read
DROP POLICY IF EXISTS allow_user_read ON public.jobs_jobsavedbyuser;
CREATE POLICY allow_user_read ON public.jobs_jobsavedbyuser
  FOR SELECT
  USING (candidate_id = (select auth.uid()));

-- 2i. jobs_jobsavedbyuser.allow_user_insert
DROP POLICY IF EXISTS allow_user_insert ON public.jobs_jobsavedbyuser;
CREATE POLICY allow_user_insert ON public.jobs_jobsavedbyuser
  FOR INSERT
  WITH CHECK (candidate_id = (select auth.uid()));

-- 2j. jobs_jobsavedbyuser.allow_user_delete
DROP POLICY IF EXISTS allow_user_delete ON public.jobs_jobsavedbyuser;
CREATE POLICY allow_user_delete ON public.jobs_jobsavedbyuser
  FOR DELETE
  USING (candidate_id = (select auth.uid()));

-- 2k. token_blacklist_blacklistedtoken.allow_authenticated_read
DROP POLICY IF EXISTS allow_authenticated_read ON public.token_blacklist_blacklistedtoken;
CREATE POLICY allow_authenticated_read ON public.token_blacklist_blacklistedtoken
  FOR SELECT
  TO authenticated
  USING (true);

-- 2l. token_blacklist_blacklistedtoken.allow_service_delete
DROP POLICY IF EXISTS allow_service_delete ON public.token_blacklist_blacklistedtoken;
CREATE POLICY allow_service_delete ON public.token_blacklist_blacklistedtoken
  FOR DELETE
  TO authenticated
  USING (false);

-- 2m. token_blacklist_outstandingtoken.allow_authenticated_read
DROP POLICY IF EXISTS allow_authenticated_read ON public.token_blacklist_outstandingtoken;
CREATE POLICY allow_authenticated_read ON public.token_blacklist_outstandingtoken
  FOR SELECT
  TO authenticated
  USING (true);

-- 2n. token_blacklist_outstandingtoken.allow_user_delete
DROP POLICY IF EXISTS allow_user_delete ON public.token_blacklist_outstandingtoken;
CREATE POLICY allow_user_delete ON public.token_blacklist_outstandingtoken
  FOR DELETE
  USING (user_id = (select auth.uid()));

-- 2o. users_emailverificationtoken.allow_user_read_self
DROP POLICY IF EXISTS allow_user_read_self ON public.users_emailverificationtoken;
CREATE POLICY allow_user_read_self ON public.users_emailverificationtoken
  FOR SELECT
  USING (user_id = (select auth.uid()));

-- 2p. users_emailverificationtoken.allow_user_insert
DROP POLICY IF EXISTS allow_user_insert ON public.users_emailverificationtoken;
CREATE POLICY allow_user_insert ON public.users_emailverificationtoken
  FOR INSERT
  WITH CHECK (user_id = (select auth.uid()));

-- 2q. users_user.allow_user_read_self
DROP POLICY IF EXISTS allow_user_read_self ON public.users_user;
CREATE POLICY allow_user_read_self ON public.users_user
  FOR SELECT
  USING (id = (select auth.uid()));

-- 2r. users_userprofile.allow_user_read_self
DROP POLICY IF EXISTS allow_user_read_self ON public.users_userprofile;
CREATE POLICY allow_user_read_self ON public.users_userprofile
  FOR SELECT
  USING (user_id = (select auth.uid()));

-- 2s. users_user_groups.allow_admin_all
DROP POLICY IF EXISTS allow_admin_all ON public.users_user_groups;
CREATE POLICY allow_admin_all ON public.users_user_groups
  FOR ALL
  TO authenticated
  USING (((select auth.jwt()) ->> 'role'::text) = 'admin'::text);

-- 2t. users_user_user_permissions.allow_admin_all
DROP POLICY IF EXISTS allow_admin_all ON public.users_user_user_permissions;
CREATE POLICY allow_admin_all ON public.users_user_user_permissions
  FOR ALL
  TO authenticated
  USING (((select auth.jwt()) ->> 'role'::text) = 'admin'::text);


-- ============================================================
-- FIX 3: PERFORMANCE — duplicate_index (1)
-- Drop the duplicate index on jobs_job.employer_id
-- ============================================================
DROP INDEX IF EXISTS public.jobs_job_employe_da1c9a_idx;


-- ============================================================
-- FIX 5: SECURITY (INFO) — rls_enabled_no_policy (7 tables)
-- Add deny-all policies for Django internal tables
-- ============================================================

CREATE POLICY deny_all ON public.auth_group FOR ALL USING (false);
CREATE POLICY deny_all ON public.auth_group_permissions FOR ALL USING (false);
CREATE POLICY deny_all ON public.auth_permission FOR ALL USING (false);
CREATE POLICY deny_all ON public.django_admin_log FOR ALL USING (false);
CREATE POLICY deny_all ON public.django_content_type FOR ALL USING (false);
CREATE POLICY deny_all ON public.django_migrations FOR ALL USING (false);
CREATE POLICY deny_all ON public.django_session FOR ALL USING (false);
