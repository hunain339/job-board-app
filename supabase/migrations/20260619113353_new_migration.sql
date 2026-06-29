-- Private resume bucket and storage hardening
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'cv-savage',
  'cv-savage',
  false,
  5242880,
  array[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
)
on conflict (id) do update
set name = excluded.name,
    public = excluded.public,
    file_size_limit = excluded.file_size_limit,
    allowed_mime_types = excluded.allowed_mime_types,
    updated_at = now();

-- Defense in depth for exposed tables
alter table public.django_content_type enable row level security;
alter table public.auth_permission enable row level security;
alter table public.auth_group enable row level security;
alter table public.auth_group_permissions enable row level security;
alter table public.users_user enable row level security;
alter table public.users_user_groups enable row level security;
alter table public.users_user_user_permissions enable row level security;
alter table public.users_emailverificationtoken enable row level security;
alter table public.users_userprofile enable row level security;
alter table public.django_admin_log enable row level security;
alter table public.jobs_job enable row level security;
alter table public.jobs_jobcategory enable row level security;
alter table public.jobs_jobsavedbyuser enable row level security;
alter table public.applications_application enable row level security;
alter table public.applications_applicationnote enable row level security;
alter table public.applications_applicationstatushistory enable row level security;
alter table public.django_session enable row level security;
alter table public.django_migrations enable row level security;
