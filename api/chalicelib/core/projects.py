import json
from typing import Optional

from fastapi import HTTPException, status

import schemas
from chalicelib.core import users
from chalicelib.utils import pg_client, helper
from chalicelib.utils.TimeUTC import TimeUTC


def __exists_by_name(name: str, exclude_id: Optional[int]) -> bool:
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify(f"""SELECT EXISTS(SELECT 1
                                FROM public.projects
                                WHERE deleted_at IS NULL
                                    AND name ILIKE %(name)s
                                    {"AND project_id!=%(exclude_id)s" if exclude_id else ""}) AS exists;""",
                            {"name": name, "exclude_id": exclude_id})

        cur.execute(query=query)
        row = cur.fetchone()
        return row["exists"]


def __update(tenant_id, project_id, changes):
    if len(changes.keys()) == 0:
        return None

    sub_query = []
    for key in changes.keys():
        sub_query.append(f"{helper.key_to_snake_case(key)} = %({key})s")
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify(f"""UPDATE public.projects 
                                SET {" ,".join(sub_query)} 
                                WHERE project_id = %(project_id)s
                                    AND deleted_at ISNULL
                                RETURNING project_id,name,gdpr;""",
                            {"project_id": project_id, **changes})
        cur.execute(query=query)
        return helper.dict_to_camel_case(cur.fetchone())


def __create(tenant_id, name):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify(f"""INSERT INTO public.projects (name, active)
                                VALUES (%(name)s,TRUE)
                                RETURNING project_id;""",
                            {"name": name})
        cur.execute(query=query)
        project_id = cur.fetchone()["project_id"]
    return get_project(tenant_id=tenant_id, project_id=project_id, include_gdpr=True)


def get_projects(tenant_id, gdpr=None):
    with pg_client.PostgresClient() as cur:
        extra_projection = ",'green' AS status,TRUE as recorded"
        if gdpr:
            extra_projection += ',s.gdpr'

        query = cur.mogrify(f"""SELECT s.project_id, s.name, s.project_key, s.save_request_payloads, s.first_recorded_session_at,
                                       created_at {extra_projection}
                                FROM public.projects AS s
                                WHERE s.deleted_at IS NULL
                                ORDER BY s.name;""")
        cur.execute(query)
        rows = cur.fetchall()
        for r in rows:
            r["created_at"] = TimeUTC.datetime_to_timestamp(r["created_at"])

        return helper.list_to_camel_case(rows)


def get_project(tenant_id, project_id, include_last_session=False, include_gdpr=None):
    with pg_client.PostgresClient() as cur:
        extra_select = ""
        if include_last_session:
            extra_select += """,(SELECT max(ss.start_ts) 
                                 FROM public.sessions AS ss 
                                 WHERE ss.project_id = %(project_id)s) AS last_recorded_session_at"""
        if include_gdpr:
            extra_select += ",s.gdpr"
        query = cur.mogrify(f"""SELECT s.project_id,
                                       s.project_key,
                                       s.name,
                                       s.save_request_payloads
                                       {extra_select}
                                FROM public.projects AS s
                                WHERE s.project_id =%(project_id)s
                                    AND s.deleted_at IS NULL
                                LIMIT 1;""",
                            {"project_id": project_id})
        cur.execute(query=query)
        row = cur.fetchone()
        return helper.dict_to_camel_case(row)


def get_project_by_key(tenant_id, project_key, include_last_session=False, include_gdpr=None):
    with pg_client.PostgresClient() as cur:
        extra_select = ""
        if include_last_session:
            extra_select += """,(SELECT max(ss.start_ts) 
                                 FROM public.sessions AS ss 
                                 WHERE ss.project_key = %(project_key)s) AS last_recorded_session_at"""
        if include_gdpr:
            extra_select += ",s.gdpr"
        query = cur.mogrify(f"""SELECT s.project_key,
                                       s.name
                                       {extra_select}
                                FROM public.projects AS s
                                WHERE s.project_key =%(project_key)s
                                    AND s.deleted_at IS NULL
                                LIMIT 1;""",
                            {"project_key": project_key})
        cur.execute(query=query)
        row = cur.fetchone()
        return helper.dict_to_camel_case(row)


def create(tenant_id, user_id, data: schemas.CreateProjectSchema, skip_authorization=False):
    if __exists_by_name(name=data.name, exclude_id=None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"name already exists.")
    if not skip_authorization:
        admin = users.get(user_id=user_id, tenant_id=tenant_id)
        if not admin["admin"] and not admin["superAdmin"]:
            return {"errors": ["unauthorized"]}
    return {"data": __create(tenant_id=tenant_id, name=data.name)}


def edit(tenant_id, user_id, project_id, data: schemas.CreateProjectSchema):
    if __exists_by_name(name=data.name, exclude_id=project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"name already exists.")
    admin = users.get(user_id=user_id, tenant_id=tenant_id)
    if not admin["admin"] and not admin["superAdmin"]:
        return {"errors": ["unauthorized"]}
    return {"data": __update(tenant_id=tenant_id, project_id=project_id,
                             changes={"name": data.name})}


def delete(tenant_id, user_id, project_id):
    admin = users.get(user_id=user_id, tenant_id=tenant_id)

    if not admin["admin"] and not admin["superAdmin"]:
        return {"errors": ["unauthorized"]}
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""UPDATE public.projects 
                               SET deleted_at = timezone('utc'::text, now()),
                                   active = FALSE
                               WHERE project_id = %(project_id)s;""",
                            {"project_id": project_id})
        cur.execute(query=query)
    return {"data": {"state": "success"}}


def get_gdpr(project_id):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""SELECT gdpr
                               FROM public.projects AS s
                               WHERE s.project_id =%(project_id)s
                                    AND s.deleted_at IS NULL;""",
                            {"project_id": project_id})
        cur.execute(query=query)
        row = cur.fetchone()["gdpr"]
        row["projectId"] = project_id
        return row


def edit_gdpr(project_id, gdpr):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""UPDATE public.projects 
                               SET gdpr = gdpr|| %(gdpr)s
                               WHERE project_id = %(project_id)s 
                                    AND deleted_at ISNULL
                               RETURNING gdpr;""",
                            {"project_id": project_id, "gdpr": json.dumps(gdpr)})
        cur.execute(query=query)
        row = cur.fetchone()
        if not row:
            return {"errors": ["something went wrong"]}
        row = row["gdpr"]
        row["projectId"] = project_id
        return row


def get_internal_project_id(project_key):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""SELECT project_id
                               FROM public.projects
                               WHERE project_key =%(project_key)s 
                                    AND deleted_at ISNULL;""",
                            {"project_key": project_key})
        cur.execute(query=query)
        row = cur.fetchone()
        return row["project_id"] if row else None


def get_project_key(project_id):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""SELECT project_key
                               FROM public.projects
                               WHERE project_id =%(project_id)s
                                    AND deleted_at ISNULL;""",
                            {"project_id": project_id})
        cur.execute(query=query)
        project = cur.fetchone()
        return project["project_key"] if project is not None else None


def get_capture_status(project_id):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""SELECT sample_rate AS rate, sample_rate=100 AS capture_all
                               FROM public.projects
                               WHERE project_id =%(project_id)s 
                                    AND deleted_at ISNULL;""",
                            {"project_id": project_id})
        cur.execute(query=query)
        return helper.dict_to_camel_case(cur.fetchone())


def update_capture_status(project_id, changes):
    if "rate" not in changes and "captureAll" not in changes:
        return {"errors": ["please provide 'rate' and/or 'captureAll' attributes to update."]}
    if int(changes["rate"]) < 0 or int(changes["rate"]) > 100:
        return {"errors": ["'rate' must be between 0..100."]}
    sample_rate = 0
    if "rate" in changes:
        sample_rate = int(changes["rate"])
    if changes.get("captureAll"):
        sample_rate = 100
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify("""UPDATE public.projects
                               SET sample_rate= %(sample_rate)s
                               WHERE project_id =%(project_id)s
                                    AND deleted_at ISNULL;""",
                            {"project_id": project_id, "sample_rate": sample_rate})
        cur.execute(query=query)

    return changes


def get_projects_ids(tenant_id):
    with pg_client.PostgresClient() as cur:
        query = f"""SELECT s.project_id
                    FROM public.projects AS s
                    WHERE s.deleted_at IS NULL
                    ORDER BY s.project_id;"""
        cur.execute(query=query)
        rows = cur.fetchall()
    return [r["project_id"] for r in rows]
