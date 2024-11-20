# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.
import abc
import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api_app.analyzers_manager.constants import ObservableTypes
from api_app.analyzers_manager.models import AnalyzerConfig
from api_app.models import Comment, Job, Parameter, PluginConfig, Tag
from certego_saas.apps.organization.membership import Membership
from certego_saas.apps.organization.organization import Organization

from .. import CustomViewSetTestCase, ViewSetTestCaseMixin

User = get_user_model()


class CommentViewSetTestCase(CustomViewSetTestCase):
    comment_url = reverse("comments-list")

    def setUp(self):
        super().setUp()
        self.job = Job.objects.create(
            user=self.superuser,
            is_sample=False,
            observable_name="8.8.8.8",
            observable_classification=ObservableTypes.IP,
        )
        self.job2 = Job.objects.create(
            user=self.superuser,
            is_sample=False,
            observable_name="8.8.8.8",
            observable_classification=ObservableTypes.IP,
        )
        self.comment = Comment.objects.create(
            job=self.job, user=self.superuser, content="test"
        )
        self.comment.save()

    def tearDown(self) -> None:
        super().tearDown()
        self.job.delete()
        self.job2.delete()
        self.comment.delete()

    def test_list_200(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 1)

    def test_create_201(self):
        data = {"job_id": self.job.id, "content": "test2"}
        response = self.client.post(self.comment_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get("content"), "test2")

    def test_delete(self):
        response = self.client.delete(f"{self.comment_url}/{self.comment.pk}")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.superuser)
        response = self.client.delete(f"{self.comment_url}/{self.comment.pk}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Comment.objects.all().count())

    def test_get(self):
        response = self.client.get(f"{self.comment_url}/{self.comment.pk}")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.superuser)
        response = self.client.get(f"{self.comment_url}/{self.comment.pk}")
        self.assertEqual(response.status_code, 200)


class JobViewSetTests(CustomViewSetTestCase):
    jobs_list_uri = reverse("jobs-list")
    jobs_recent_scans_uri = reverse("jobs-recent-scans")
    jobs_recent_scans_user_uri = reverse("jobs-recent-scans-user")
    agg_status_uri = reverse("jobs-aggregate-status")
    agg_type_uri = reverse("jobs-aggregate-type")
    agg_observable_classification_uri = reverse(
        "jobs-aggregate-observable-classification"
    )
    agg_file_mimetype_uri = reverse("jobs-aggregate-file-mimetype")
    agg_observable_name_uri = reverse("jobs-aggregate-observable-name")
    agg_file_name_uri = reverse("jobs-aggregate-md5")

    def setUp(self):
        super().setUp()
        self.job, _ = Job.objects.get_or_create(
            **{
                "user": self.superuser,
                "is_sample": False,
                "observable_name": "1.2.3.4",
                "observable_classification": "ip",
            }
        )
        self.job2, _ = Job.objects.get_or_create(
            **{
                "user": self.superuser,
                "is_sample": True,
                "md5": "test.file",
                "file_name": "test.file",
                "file_mimetype": "application/vnd.microsoft.portable-executable",
            }
        )

    def test_recent_scan(self):
        j1 = Job.objects.create(
            **{
                "user": self.user,
                "is_sample": False,
                "observable_name": "gigatest.com",
                "observable_classification": "domain",
                "finished_analysis_time": now() - datetime.timedelta(days=2),
            }
        )
        j2 = Job.objects.create(
            **{
                "user": self.user,
                "is_sample": False,
                "observable_name": "gigatest.com",
                "observable_classification": "domain",
                "finished_analysis_time": now() - datetime.timedelta(hours=2),
            }
        )
        response = self.client.post(self.jobs_recent_scans_uri, data={"md5": j1.md5})
        content = response.json()
        msg = (response, content)
        self.assertEqual(200, response.status_code, msg=msg)
        self.assertIsInstance(content, list)
        pks = [elem["pk"] for elem in content]
        self.assertIn(j2.pk, pks)
        self.assertIn(j1.pk, pks)

        j1.delete()
        j2.delete()

    def test_recent_scan_user(self):
        j1 = Job.objects.create(
            **{
                "user": self.user,
                "is_sample": False,
                "observable_name": "gigatest.com",
                "observable_classification": "domain",
                "finished_analysis_time": now() - datetime.timedelta(days=2),
            }
        )
        j2 = Job.objects.create(
            **{
                "user": self.superuser,
                "is_sample": False,
                "observable_name": "gigatest.com",
                "observable_classification": "domain",
                "finished_analysis_time": now() - datetime.timedelta(hours=2),
            }
        )
        response = self.client.post(
            self.jobs_recent_scans_user_uri, data={"is_sample": False}
        )
        content = response.json()
        msg = (response, content)
        self.assertEqual(200, response.status_code, msg=msg)
        self.assertIsInstance(content, list)
        pks = [elem["pk"] for elem in content]
        self.assertIn(j1.pk, pks)
        self.assertNotIn(j2.pk, pks)

        j1.delete()
        j2.delete()

    def test_list_200(self):
        response = self.client.get(self.jobs_list_uri)
        content = response.json()
        msg = (response, content)

        self.assertEqual(200, response.status_code, msg=msg)
        self.assertIn("count", content, msg=msg)
        self.assertIn("total_pages", content, msg=msg)
        self.assertIn("results", content, msg=msg)

    def test_retrieve_200(self):
        response = self.client.get(f"{self.jobs_list_uri}/{self.job.id}")
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content["id"], self.job.id, msg=msg)
        self.assertEqual(content["status"], self.job.status, msg=msg)

    def test_delete(self):
        self.assertEqual(Job.objects.count(), 2)
        response = self.client.delete(f"{self.jobs_list_uri}/{self.job.id}")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=self.job.user)
        response = self.client.delete(f"{self.jobs_list_uri}/{self.job.id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Job.objects.count(), 1)

    # @action endpoints

    def test_kill(self):
        job = Job.objects.create(status=Job.Status.RUNNING, user=self.superuser)
        self.assertEqual(job.status, Job.Status.RUNNING)
        uri = reverse("jobs-kill", args=[job.pk])
        response = self.client.patch(uri)

        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(user=self.job.user)
        response = self.client.patch(uri)
        self.assertEqual(response.status_code, 204)
        job.refresh_from_db()

        self.assertEqual(job.status, Job.Status.KILLED)

    def test_kill_400(self):
        # create a new job whose status is not "running"
        job = Job.objects.create(
            status=Job.Status.REPORTED_WITHOUT_FAILS, user=self.superuser
        )
        uri = reverse("jobs-kill", args=[job.pk])
        self.client.force_authenticate(user=self.job.user)
        response = self.client.patch(uri)
        content = response.json()
        msg = (response, content)
        self.assertEqual(response.status_code, 400, msg=msg)
        self.assertDictEqual(
            content["errors"], {"detail": "Job is not running"}, msg=msg
        )

    # aggregation endpoints

    def test_agg_status_200(self):
        resp = self.client.get(self.agg_status_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        for field in ["date", *Job.Status.values]:
            self.assertIn(
                field,
                content[0],
                msg=msg,
            )

    def test_agg_type_200(self):
        resp = self.client.get(self.agg_type_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        self.assertEqual(resp.status_code, 200, msg)
        for field in ["date", "file", "observable"]:
            self.assertIn(
                field,
                content[0],
                msg=msg,
            )

    def test_agg_observable_classification_200(self):
        resp = self.client.get(self.agg_observable_classification_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        for field in ["date", *ObservableTypes.values]:
            self.assertIn(
                field,
                content[0],
                msg=msg,
            )

    def test_agg_file_mimetype_200(self):
        resp = self.client.get(self.agg_file_mimetype_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        for field in ["date", *content["values"]]:
            self.assertIn(
                field,
                content["aggregation"][0],
                msg=msg,
            )

    def test_agg_observable_name_200(self):
        resp = self.client.get(self.agg_observable_name_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        for field in content["values"]:
            self.assertIn(
                field,
                content["aggregation"],
                msg=msg,
            )

    def test_agg_file_name_200(self):
        resp = self.client.get(self.agg_file_name_uri)
        content = resp.json()
        msg = (resp, content)

        self.assertEqual(resp.status_code, 200, msg)
        for field in content["values"]:
            self.assertIn(
                field,
                content["aggregation"],
                msg=msg,
            )


class TagViewsetTests(CustomViewSetTestCase):
    tags_list_uri = reverse("tags-list")

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.superuser)
        self.tag, _ = Tag.objects.get_or_create(label="testlabel1", color="#FF5733")

    def test_create_201(self):
        self.assertEqual(Tag.objects.count(), 1)
        data = {"label": "testlabel2", "color": "#91EE28"}
        response = self.client.post(self.tags_list_uri, data)
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 201, msg=msg)
        self.assertDictContainsSubset(data, content, msg=msg)
        self.assertEqual(Tag.objects.count(), 2)

    def test_create_400(self):
        self.assertEqual(Tag.objects.count(), 1)
        data = {"label": "testlabel2", "color": "NOT_A_COLOR"}
        response = self.client.post(self.tags_list_uri, data)
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 400, msg=msg)

    def test_list_200(self):
        response = self.client.get(self.tags_list_uri)
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 200, msg=msg)

    def test_retrieve_200(self):
        response = self.client.get(f"{self.tags_list_uri}/{self.tag.id}")
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 200, msg=msg)

    def test_update_200(self):
        new_data = {"label": "newTestLabel", "color": "#765A54"}
        response = self.client.put(f"{self.tags_list_uri}/{self.tag.id}", new_data)
        content = response.json()
        msg = (response, content)

        self.assertEqual(response.status_code, 200, msg=msg)
        self.assertDictContainsSubset(new_data, content, msg=msg)

    def test_delete_204(self):
        self.assertEqual(Tag.objects.count(), 1)
        response = self.client.delete(f"{self.tags_list_uri}/{self.tag.id}")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Tag.objects.count(), 0)


class AbstractConfigViewSetTestCaseMixin(ViewSetTestCaseMixin, metaclass=abc.ABCMeta):
    def test_organization_disable(self):
        plugin_name = self.model_class.objects.order_by("?").first().name
        org, _ = Organization.objects.get_or_create(name="test")

        # a guest user cannot disable plugin config at org level
        response = self.client.post(f"{self.URL}/{plugin_name}/organization")
        self.assertEqual(response.status_code, 403, response.json())
        result = response.json()
        self.assertIn("detail", result)
        self.assertEqual(
            result["detail"], "You do not have permission to perform this action."
        )

        # a member cannot disable plugin config at org level
        m, _ = Membership.objects.get_or_create(
            user=self.user, organization=org, is_owner=False
        )
        response = self.client.post(f"{self.URL}/{plugin_name}/organization")
        self.assertEqual(response.status_code, 403, response.json())
        result = response.json()
        self.assertIn("detail", result)
        self.assertEqual(
            result["detail"], "You do not have permission to perform this action."
        )

        # an admin can disable plugin config at org level
        m.is_admin = True
        m.save()
        plugin = self.model_class.objects.get(name=plugin_name)
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        response = self.client.post(
            f"{self.URL}/{plugin_name}/organization"
        )  # disabling it
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            plugin.disabled_in_organizations.all().exists()
        )  # now it's disabled
        response = self.client.post(
            f"{self.URL}/{plugin_name}/organization"
        )  # try to disable it again
        self.assertEqual(response.status_code, 400, response.json())
        self.assertEqual(
            1, plugin.disabled_in_organizations.all().count()
        )  # still 1 disabled
        result = response.json()
        self.assertIn("errors", result)
        self.assertIn("detail", result["errors"])
        self.assertEqual(
            result["errors"]["detail"], f"Plugin {plugin.name} already disabled"
        )

        # an owner can disable plugin config at org level
        m.is_admin = True  # and owner is also and admin
        m.is_owner = True
        m.save()
        plugin.disabled_in_organizations.update(
            disabled=False
        )  # reset the disabled plugins
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        response = self.client.post(
            f"{self.URL}/{plugin_name}/organization"
        )  # disabling it
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            plugin.disabled_in_organizations.all().exists()
        )  # now it's disabled

        plugin.disabled_in_organizations.delete()
        m.delete()
        org.delete()

    def test_organization_enable(self):
        plugin_name = self.model_class.objects.order_by("?").first().name
        org, _ = Organization.objects.get_or_create(name="test")

        # a guest user cannot enable plugin config at org level
        response = self.client.delete(f"{self.URL}/{plugin_name}/organization")
        self.assertEqual(response.status_code, 403, response.json())
        result = response.json()
        self.assertIn("detail", result)
        self.assertEqual(
            result["detail"], "You do not have permission to perform this action."
        )

        # a member cannot enable plugin config at org level
        m, _ = Membership.objects.get_or_create(
            user=self.user, organization=org, is_owner=False
        )
        response = self.client.delete(f"{self.URL}/{plugin_name}/organization")
        result = response.json()
        self.assertEqual(response.status_code, 403, result)
        self.assertIn("detail", result)
        self.assertEqual(
            result["detail"], "You do not have permission to perform this action."
        )

        # an admin can enable plugin config at org level
        m, _ = Membership.objects.get_or_create(
            user=self.superuser, organization=org, is_owner=False
        )
        m.is_admin = True
        m.save()
        self.client.force_authenticate(m.user)
        plugin = self.model_class.objects.get(name=plugin_name)
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        response = self.client.delete(
            f"{self.URL}/{plugin_name}/organization"
        )  # enabling it
        result = response.json()
        self.assertEqual(response.status_code, 400, result)  # validation error
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        self.assertIn("errors", result)
        self.assertIn("detail", result["errors"])
        # I can enable it but is already enabled
        self.assertEqual(
            result["errors"]["detail"], f"Plugin {plugin.name} already enabled"
        )
        plugin.orgs_configuration.update(disabled=True)  # disabling it
        response = self.client.delete(
            f"{self.URL}/{plugin_name}/organization"
        )  # disable it
        self.assertEqual(response.status_code, 202)
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # is it enabled?

        # an owner can disable plugin config at org level
        m.is_owner = True
        m.is_admin = True  # an owner is also an admin
        m.save()
        plugin.disabled_in_organizations.update(disabled=False)
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        response = self.client.delete(
            f"{self.URL}/{plugin_name}/organization"
        )  # enabling it
        result = response.json()
        self.assertEqual(response.status_code, 400, result)  # validation error
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # isn't it disabled?
        self.assertIn("errors", result)
        self.assertIn("detail", result["errors"])
        # I can enable it but is already enabled
        self.assertEqual(
            result["errors"]["detail"], f"Plugin {plugin.name} already enabled"
        )
        plugin.orgs_configuration.update(disabled=True)  # disabling it
        response = self.client.delete(
            f"{self.URL}/{plugin_name}/organization"
        )  # enabling it
        self.assertEqual(response.status_code, 202)
        self.assertFalse(
            plugin.disabled_in_organizations.all().exists()
        )  # is it enabled?

        m.delete()
        org.delete()


class PluginConfigViewSetTestCase(CustomViewSetTestCase):

    def setUp(self):
        super().setUp()
        PluginConfig.objects.all().delete()

    def test_plugin_config(self):
        org = Organization.create("test_org", self.user)
        Membership.objects.create(
            user=self.admin, organization=org, is_owner=False, is_admin=True
        )
        ac = AnalyzerConfig.objects.get(name="AbuseIPDB")
        uri = f"/api/analyzer/{ac.name}/plugin_config"

        # logged out
        self.client.logout()
        response = self.client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 401)

        param = Parameter.objects.create(
            is_secret=True,
            name="mynewparameter",
            python_module=ac.python_module,
            required=True,
            type="str",
        )
        pc = PluginConfig(
            value="supersecret",
            for_organization=True,
            owner=self.user,
            parameter=param,
            analyzer_config=ac,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, org.owner)

        # if the user is owner of an org, he should get the org secret
        self.client.force_authenticate(user=self.user)
        response = self.client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in [*org_config, *user_config]:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret")

        # if the user is admin of an org, he should get the org secret
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in [*org_config, *user_config]:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret")

        # second personal item
        secret_owner = PluginConfig(
            value="supersecret_user_only",
            for_organization=False,
            owner=self.user,
            parameter=param,
            analyzer_config=ac,
        )
        secret_owner.save()

        # user can see own personal secret
        self.client.force_authenticate(user=self.user)
        response = self.client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in org_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret")
        for config in user_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret_user_only")

        # other users cannot see user's personal items
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in org_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret")
        for config in user_config:
            if config["attribute"] == "mynewparameter":
                self.assertNotEqual(config["value"], "supersecret_user_only")
                self.assertEqual(config["value"], "supersecret")

        # if a standard user who does not belong to any org tries to get a secret,
        # they should not find anything
        self.standard_user = User.objects.create_user(
            username="standard_user",
            email="standard_user@intelowl.com",
            password="test",
        )
        self.standard_user.save()
        self.standard_user_client = APIClient()
        self.standard_user_client.force_authenticate(user=self.standard_user)
        response = self.standard_user_client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]
        self.assertEqual(org_config, [])

        for config in user_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], None)

        # if a standard user tries to get the secret of his org,
        # he should have a "redacted" value
        Membership(
            user=self.standard_user, organization=org, is_owner=False, is_admin=False
        ).save()
        response = self.standard_user_client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in [*org_config, *user_config]:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "redacted")

        secret_owner.refresh_from_db()
        self.assertEqual(secret_owner.value, "supersecret_user_only")

        # third superuser secret
        secret_owner = PluginConfig(
            value="supersecret_low_privilege",
            for_organization=False,
            owner=self.standard_user,
            parameter=param,
            analyzer_config=ac,
        )
        secret_owner.save()
        response = self.standard_user_client.get(uri, {}, format="json")
        self.assertEqual(response.status_code, 200)
        content = response.json()
        org_config = content["organization_config"]
        user_config = content["user_config"]

        for config in org_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "redacted")
        for config in user_config:
            if config["attribute"] == "mynewparameter":
                self.assertEqual(config["value"], "supersecret_low_privilege")

        param.delete()
        PluginConfig.objects.filter(value__startswith="supersecret").delete()
        org.delete()

    def test_plugin_config_list(self):
        ac = AnalyzerConfig.objects.first()
        uri = f"/api/analyzer/{ac.name}/plugin_config"
        param = Parameter.objects.create(
            python_module=ac.python_module,
            name="test",
            is_secret=True,
            required=True,
            type="str",
        )
        org0 = Organization.objects.create(name="testorg0")
        org1 = Organization.objects.create(name="testorg1")
        another_owner = User.objects.create_user(
            username="another_owner",
            email="another_owner@intelowl.com",
            password="test",
        )
        another_owner.save()
        m0 = Membership.objects.create(
            organization=org0, user=self.superuser, is_owner=True
        )
        m1 = Membership.objects.create(
            organization=org0, user=self.admin, is_owner=False, is_admin=True
        )
        m2 = Membership.objects.create(
            organization=org1, user=self.user, is_owner=False, is_admin=False
        )
        m3 = Membership.objects.create(
            organization=org1, user=another_owner, is_owner=True
        )
        pc0 = PluginConfig.objects.create(
            parameter=param,
            analyzer_config=ac,
            value="value",
            owner=self.superuser,
            for_organization=True,
        )
        pc1 = PluginConfig.objects.create(
            parameter=param,
            analyzer_config=ac,
            value="value",
            owner=another_owner,
            for_organization=True,
        )
        # logged out
        self.client.logout()
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 401)

        # the owner can see the config of own org
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        org_config = result["organization_config"]
        needle = None
        for obj in org_config:
            if obj["attribute"] == pc0.attribute:
                needle = obj
            # the owner cannot see configs of other orgs (pc1)
            if "organization" in obj.keys():
                self.assertEqual(obj["organization"], "testorg0")
        self.assertIsNotNone(needle)
        self.assertIn("type", needle)
        self.assertEqual(needle["type"], param.type)
        self.assertIn("organization", needle)
        self.assertEqual(needle["organization"], "testorg0")
        self.assertIn("value", needle)
        self.assertEqual(needle["value"], "value")
        self.assertIn("attribute", needle)
        self.assertEqual(needle["attribute"], "test")
        self.assertIn("required", needle)
        self.assertEqual(needle["required"], param.required)
        self.assertIn("is_secret", needle)
        self.assertEqual(needle["is_secret"], param.is_secret)

        # an admin can see the config of own org
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        org_config = result["organization_config"]
        needle = None
        for obj in org_config:
            if obj["attribute"] == pc0.attribute:
                needle = obj
            # an admin cannot see configs of other orgs (pc1)
            if "organization" in obj.keys():
                self.assertEqual(obj["organization"], "testorg0")
        self.assertIsNotNone(needle)
        self.assertIn("type", needle)
        self.assertEqual(needle["type"], param.type)
        self.assertIn("organization", needle)
        self.assertEqual(needle["organization"], "testorg0")
        self.assertIn("value", needle)
        self.assertEqual(needle["value"], "value")
        self.assertIn("attribute", needle)
        self.assertEqual(needle["attribute"], "test")
        self.assertIn("required", needle)
        self.assertEqual(needle["required"], param.required)
        self.assertIn("is_secret", needle)
        self.assertEqual(needle["is_secret"], param.is_secret)

        # a user in the org can see the config with redacted data
        self.client.force_authenticate(user=self.user)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        org_config = result["organization_config"]
        needle = None
        for obj in org_config:
            if obj["attribute"] == pc1.attribute:
                needle = obj
            # a user cannot see configs of other orgs (pc0)
            if "organization" in obj.keys():
                self.assertEqual(obj["organization"], "testorg1")
        self.assertIsNotNone(needle)
        self.assertIn("type", needle)
        self.assertEqual(needle["type"], param.type)
        self.assertIn("organization", needle)
        self.assertEqual(needle["organization"], "testorg1")
        self.assertIn("value", needle)
        self.assertEqual(needle["value"], "redacted")
        self.assertIn("attribute", needle)
        self.assertEqual(needle["attribute"], "test")
        self.assertIn("required", needle)
        self.assertEqual(needle["required"], param.required)
        self.assertIn("is_secret", needle)
        self.assertEqual(needle["is_secret"], param.is_secret)

        # a user outside the org can not see the config
        self.client.force_authenticate(user=self.guest)
        response = self.client.get(uri)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        org_config = result["organization_config"]
        self.assertEqual(org_config, [])
        m0.delete()
        m1.delete()
        m2.delete()
        m3.delete()
        another_owner.delete()
        org0.delete()
        org1.delete()
        param.delete()

    def test_update(self):
        org = Organization.create("test_org", self.superuser)
        Membership.objects.create(
            user=self.admin, organization=org, is_owner=False, is_admin=True
        )
        Membership.objects.create(
            user=self.user, organization=org, is_owner=False, is_admin=False
        )
        ac = AnalyzerConfig.objects.get(name="AbuseIPDB")
        uri = f"/api/analyzer/{ac.name}/plugin_config"

        # logged out
        self.client.logout()
        response = self.client.patch(uri, {}, format="json")
        self.assertEqual(response.status_code, 401)

        param = Parameter.objects.create(
            is_secret=True,
            name="mynewparameter",
            python_module=ac.python_module,
            required=True,
            type="str",
        )
        pc = PluginConfig(
            value="supersecret",
            for_organization=True,
            owner=self.superuser,
            parameter=param,
            analyzer_config=ac,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, org.owner)

        # owner can update org secret
        self.client.force_authenticate(user=self.superuser)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret",
                "organization": "test_org",
            }
        ]
        response = self.client.patch(uri, payload, format="json")
        self.assertEqual(response.status_code, 200)
        pc1 = PluginConfig.objects.get(id=pc.pk)
        self.assertEqual(pc1.value, "new_org_supersecret")

        # admin can update org secret
        self.client.force_authenticate(user=self.admin)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret_admin",
                "organization": "test_org",
            }
        ]
        response = self.client.patch(uri, payload, format="json")
        self.assertEqual(response.status_code, 200)
        pc1 = PluginConfig.objects.get(id=pc.pk)
        self.assertEqual(pc1.value, "new_org_supersecret_admin")

        # user can not update org secret
        self.client.force_authenticate(user=self.user)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret_user",
                "organization": "test_org",
            }
        ]
        response = self.client.patch(uri, payload, format="json")
        self.assertEqual(response.status_code, 403)

        # second personal item
        secret_owner = PluginConfig(
            value="supersecret_user_only",
            for_organization=False,
            owner=self.user,
            parameter=param,
            analyzer_config=ac,
        )
        secret_owner.save()

        # user can update own personal secret
        self.client.force_authenticate(user=self.user)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_supersecret_user_only",
            }
        ]

        response = self.client.patch(uri, payload, format="json")
        self.assertEqual(response.status_code, 200)
        pc_user = PluginConfig.objects.get(id=secret_owner.pk)
        self.assertEqual(pc_user.value, "new_supersecret_user_only")

        # other users cannot update user's personal items
        self.client.force_authenticate(user=self.admin)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_supersecret_admin_only",
            }
        ]
        response = self.client.patch(uri, payload, format="json")
        self.assertEqual(response.status_code, 403)
        pc_user = PluginConfig.objects.get(id=secret_owner.pk)
        self.assertEqual(pc_user.value, "new_supersecret_user_only")
        self.assertNotEqual(pc_user.value, "new_supersecret_admin_only")

        secret_owner.delete()
        pc.delete()

        param.delete()
        PluginConfig.objects.filter(value__startswith="supersecret").delete()
        org.delete()

    def test_create(self):
        org = Organization.create("test_org", self.superuser)
        Membership.objects.create(
            user=self.admin, organization=org, is_owner=False, is_admin=True
        )
        Membership.objects.create(
            user=self.user, organization=org, is_owner=False, is_admin=False
        )
        ac = AnalyzerConfig.objects.get(name="AbuseIPDB")
        uri = f"/api/analyzer/{ac.name}/plugin_config"

        # logged out
        self.client.logout()
        response = self.client.patch(uri, {}, format="json")
        self.assertEqual(response.status_code, 401)

        param = Parameter.objects.create(
            is_secret=True,
            name="mynewparameter",
            python_module=ac.python_module,
            required=True,
            type="str",
        )

        # owner can create org secret
        self.client.force_authenticate(user=self.superuser)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret",
                "organization": "test_org",
            }
        ]
        response = self.client.post(uri, payload, format="json")
        self.assertEqual(response.status_code, 201)
        content = response.json()
        self.assertEqual(content[0]["value"], "new_org_supersecret")
        self.assertEqual(content[0]["owner"], self.superuser.username)
        pc = PluginConfig.objects.get(id=content[0]["id"])
        self.assertTrue(pc.for_organization)
        pc.delete()

        # admin can create org secret
        self.client.force_authenticate(user=self.admin)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret_admin",
                "organization": "test_org",
            }
        ]
        response = self.client.post(uri, payload, format="json")
        self.assertEqual(response.status_code, 201)
        content = response.json()
        self.assertEqual(content[0]["value"], "new_org_supersecret_admin")
        self.assertEqual(content[0]["owner"], self.admin.username)
        pc = PluginConfig.objects.get(id=content[0]["id"])
        self.assertTrue(pc.for_organization)
        pc.delete()

        # user can not create org secret
        self.client.force_authenticate(user=self.user)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_org_supersecret_user",
                "organization": "test_org",
            }
        ]
        response = self.client.post(uri, payload, format="json")
        self.assertEqual(response.status_code, 403)

        # user can create own personal secret
        self.client.force_authenticate(user=self.user)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_supersecret_user_only",
            }
        ]
        response = self.client.post(uri, payload, format="json")
        self.assertEqual(response.status_code, 201)
        content = response.json()
        self.assertEqual(content[0]["value"], "new_supersecret_user_only")
        self.assertEqual(content[0]["owner"], self.user.username)
        pc = PluginConfig.objects.get(id=content[0]["id"])
        self.assertFalse(pc.for_organization)
        pc.delete()

        pc = PluginConfig(
            value="default_secret",
            for_organization=False,
            owner=None,
            parameter=param,
            analyzer_config=ac,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, None)
        self.assertFalse(pc.for_organization)

        self.client.force_authenticate(user=self.user)
        payload = [
            {
                "attribute": "mynewparameter",
                "value": "new_user_secret",
            }
        ]

        response = self.client.post(uri, payload, format="json")
        self.assertEqual(response.status_code, 201)
        content = response.json()
        self.assertEqual(content[0]["value"], "new_user_secret")
        self.assertEqual(content[0]["owner"], self.user.username)
        pc1 = PluginConfig.objects.get(id=content[0]["id"])
        self.assertFalse(pc1.for_organization)
        self.assertNotEqual(pc1.id, pc.id)

        pc.delete()
        param.delete()
        PluginConfig.objects.filter(value__startswith="supersecret").delete()
        org.delete()

    def test_delete(self):
        org = Organization.create("test_org", self.superuser)
        Membership.objects.create(
            user=self.admin, organization=org, is_owner=False, is_admin=True
        )
        Membership.objects.create(
            user=self.user, organization=org, is_owner=False, is_admin=False
        )
        ac = AnalyzerConfig.objects.get(name="AbuseIPDB")
        uri = "/api/plugin-config/1"

        # logged out
        self.client.logout()
        response = self.client.delete(uri, {}, format="json")
        self.assertEqual(response.status_code, 401)

        param = Parameter.objects.create(
            is_secret=True,
            name="mynewparameter",
            python_module=ac.python_module,
            required=True,
            type="str",
        )
        pc = PluginConfig(
            value="supersecret",
            for_organization=True,
            owner=self.superuser,
            parameter=param,
            analyzer_config=ac,
            id=1,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, org.owner)

        # user can not delete org secret
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(uri, {}, format="json")
        self.assertEqual(response.status_code, 403)

        # owner can delete org secret
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(uri, format="json")
        self.assertEqual(response.status_code, 204)

        pc = PluginConfig(
            value="supersecret",
            for_organization=True,
            owner=self.superuser,
            parameter=param,
            analyzer_config=ac,
            id=1,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, org.owner)

        # admin can delete org secret
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(uri, {}, format="json")
        self.assertEqual(response.status_code, 204)

        pc = PluginConfig(
            value="supersecret",
            for_organization=False,
            owner=self.user,
            parameter=param,
            analyzer_config=ac,
            id=1,
        )
        pc.full_clean()
        pc.save()
        self.assertEqual(pc.owner, self.user)

        # user can delete own personal secret
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(uri, {}, format="json")
        self.assertEqual(response.status_code, 204)
