import logging
import re
import threading
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from travis import TravisCLient
from pprint import pprint

logger = logging.getLogger(__name__)


class TravisExtension(Extension):
    """ Main extension class """

    def __init__(self):
        logger.info('Initializing Travis Extension')
        super(TravisExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.travis_client = TravisCLient()

    def list_repos(self, query):
        """ Lists the Repositories from the user """

        try:
            repos = self.travis_client.get_repos(query)
        except Exception as e:
            return self.handle_errors(e)

        if not repos:
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name='No Repositories found',
                on_enter=HideWindowAction())
            ])

        items = []
        for repo in repos[:8]:
            desc = ''
            if repo['description']:
                desc = repo['description']

            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=repo['name'],
                description=desc,
                on_enter=SetUserQueryAction("%s %s builds" % (
                    self.preferences["kw"], repo['id'])),
                on_alt_enter=OpenUrlAction(repo['url'])
            ))

        return RenderResultListAction(items)

    def show_builds_for_repo(self, repo_id):
        """ Show the latest build results for the specified repository """

        try:
            builds = self.travis_client.get_builds_for_repo(repo_id)
        except Exception as e:
            return self.handle_errors(e)

        if not builds:
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name='No builds found for the specified repository',
                highlightable=False,
                on_enter=HideWindowAction())
            ])

        items = []
        for build in builds:

            items.append(ExtensionResultItem(
                icon=self.get_icon_for_build(build['state']),
                name='#%s - %s' % (build['number'], build['commit_message']),
                description='Branch: %s | Started by: %s | Updated: %s' % (
                    build['branch'], build['triggered_by'], build['updated_at']),
                on_enter=OpenUrlAction(build['url']),
                highlightable=False,
            ))

        return RenderResultListAction(items)

    def get_icon_for_build(self, state):
        """ Returns the build icon based on the build state """

        if state == 'passed':
            return 'images/icon_build_passed.png'

        if state == 'failed':
            return 'images/icon_build_failed.png'

        return 'images/icon_build_pending.png'

    def handle_errors(self, e):
        """ Handle errors """
        return RenderResultListAction([ExtensionResultItem(
            icon='images/icon.png',
            name='An error occurred:',
            description=e.message,
            highlightable=False,
            on_enter=HideWindowAction())
        ])


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):

        query = event.get_argument()

        if query:
            build_match = re.findall(r"^(\d+)\sbuilds$", query, re.IGNORECASE)

            if build_match:
                return extension.show_builds_for_repo(build_match[0])

        return extension.list_repos(query)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.travis_client.set_access_token(
            event.preferences['access_token'])


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'access_token':
            extension.travis_client.set_access_token(
                event.new_value)


if __name__ == '__main__':
    TravisExtension().run()
