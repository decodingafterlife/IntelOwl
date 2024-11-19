export const mockedUseAuthStore = {
  loading: false,
  token: null,
  user: {
    username: "test",
    full_name: "test user",
    first_name: "test",
    last_name: "user",
    email: "test@google.com",
  },
  access: {
    total_submissions: 10,
    month_submissions: 2,
  },
  isAuthenticated: () => true,
  updateToken: () => {},
  deleteToken: () => {},
  service: {
    fetchUserAccess: () => {},
    loginUser: () => {},
    logoutUser: () => {},
    forceLogout: () => {},
  },
};

export const mockedUseAuthStoreNoAuth = {
  loading: false,
  token: null,
  user: {},
  access: {},
  isAuthenticated: () => false,
  updateToken: () => {},
  deleteToken: () => {},
  service: {
    fetchUserAccess: () => {},
    loginUser: () => {},
    logoutUser: () => {},
    forceLogout: () => {},
  },
};

export const mockedUseOrganizationStoreNoOrg = {
  loading: false,
  error: null,
  isUserOwner: false,
  isInOrganization: false,
  organization: {},
  membersCount: undefined,
  members: [],
  pendingInvitations: [],
  pluginsState: {},
  fetchAll: () => {},
  isUserAdmin: () => true,
};

export const mockedUseOrganizationStoreUser = {
  loading: false,
  error: null,
  isUserOwner: false,
  isInOrganization: true,
  organization: {
    owner: {
      full_name: "user owner",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_owner",
      is_admin: true,
    },
    name: "org_test",
    establishedAt: "2023-10-18T14:34:38.263483Z",
  },
  membersCount: 3,
  members: [
    {
      full_name: "user owner",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_owner",
      is_admin: true,
    },
    {
      full_name: "user admin",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_admin",
      is_admin: true,
    },
    {
      full_name: "user user",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_user",
      is_admin: false,
    },
  ],
  pendingInvitations: [],
  pluginsState: {},
  fetchAll: () => {},
  fetchOnlyBasicInfo: () => {},
  refetchMembers: () => {},
  refetchInvs: () => {},
  isUserAdmin: (username) => {
    if (["user_owner", "user_admin"].includes(username)) {
      return true;
    }
    return false;
  },
};

export const mockedUseOrganizationStoreOwner = {
  loading: false,
  error: null,
  isUserOwner: true,
  isInOrganization: true,
  organization: {
    owner: {
      full_name: "user owner",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_owner",
      is_admin: true,
    },
    name: "org_test",
    establishedAt: "2023-10-18T14:34:38.263483Z",
  },
  membersCount: 3,
  members: [
    {
      full_name: "user owner",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_owner",
      is_admin: true,
    },
    {
      full_name: "user admin",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_admin",
      is_admin: true,
    },
    {
      full_name: "user user",
      joined: "2023-10-19T14:34:38.263483Z",
      username: "user_user",
      is_admin: false,
    },
  ],
  pendingInvitations: [],
  pluginsState: {},
  fetchAll: () => {},
  fetchOnlyBasicInfo: () => {},
  refetchMembers: () => {},
  refetchInvs: () => {},
  isUserAdmin: (username) => {
    if (["user_owner", "user_admin"].includes(username)) {
      return true;
    }
    return false;
  },
};

export const mockedUseTagsStore = {
  loading: false,
  error: null,
  tags: [
    {
      id: 1,
      label: "test tag",
      color: "#1655D3",
    },
  ],
  list: () => {},
  create: () => {},
  update: () => {},
};

export const mockedPlaybooks = {
  TEST_PLAYBOOK_IP: {
    name: "TEST_PLAYBOOK_IP",
    type: ["ip"],
    description: "Test playbook for the IP addresses",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 2,
    scan_check_time: "02:00:00:00",
    tags: [
      {
        id: 1,
        label: "test tag",
        color: "#1655D3",
      },
    ],
    tlp: "CLEAR",
    starting: true,
  },
  TEST_PLAYBOOK_DOMAIN: {
    name: "TEST_PLAYBOOK_DOMAIN",
    type: ["domain"],
    description: "Test playbook for the domains",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 2,
    scan_check_time: "02:00:00:00",
    tags: [],
    tlp: "CLEAR",
    starting: true,
  },
  TEST_PLAYBOOK_URL: {
    name: "TEST_PLAYBOOK_URL",
    type: ["url"],
    description: "Test playbook for the URLs",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 1,
    scan_check_time: null,
    tags: [],
    tlp: "AMBER",
    starting: true,
  },
  TEST_PLAYBOOK_HASH: {
    name: "TEST_PLAYBOOK_HASH",
    type: ["hash"],
    description: "Test playbook for the hashes",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 1,
    scan_check_time: null,
    tags: [],
    tlp: "AMBER",
    starting: true,
  },
  TEST_PLAYBOOK_FILE: {
    name: "TEST_PLAYBOOK_FILE",
    type: ["file"],
    description: "Test playbook for the files",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 1,
    scan_check_time: null,
    tags: [],
    tlp: "AMBER",
    starting: true,
  },
  TEST_PLAYBOOK_GENERIC: {
    name: "TEST_PLAYBOOK_GENERIC",
    type: ["generic"],
    description: "Test playbook for the generic observables",
    disabled: false,
    runtime_configuration: {
      analyzers: {},
      connectors: {},
      visualizers: {},
    },
    analyzers: [],
    connectors: [],
    scan_mode: 1,
    scan_check_time: null,
    tags: [],
    tlp: "AMBER",
    starting: true,
  },
};

export const mockedUsePluginConfigurationStore = {
  analyzersLoading: false,
  connectorsLoading: false,
  pivotsLoading: false,
  visualizersLoading: false,
  playbooksLoading: false,
  analyzersError: null,
  connectorsError: null,
  pivotsErrors: null,
  playbooksError: null,
  visualizersError: null,
  analyzers: [
    {
      name: "TEST_ANALYZER",
      config: {
        queue: "default",
        soft_time_limit: 30,
      },
      python_module: "test.Test",
      description: "Test analyzer",
      disabled: false,
      type: "observable",
      docker_based: false,
      maximum_tlp: "AMBER",
      observable_supported: ["domain", "generic", "hash", "ip", "url", "file"],
      supported_filetypes: [],
      run_hash: false,
      run_hash_type: "",
      not_supported_filetypes: [],
      params: {
        query_type: {
          type: "str",
          description: "Test analyzer param description.",
          required: false,
          value: "AAAA",
          is_secret: false,
        },
      },
      secrets: {},
      verification: {
        configured: true,
        details: "Ready to use!",
        missing_secrets: [],
      },
      orgPluginDisabled: false,
      plugin_type: "1",
    },
  ],
  connectors: [
    {
      name: "TEST_CONNECTOR",
      config: {
        queue: "default",
        soft_time_limit: 30,
      },
      python_module: "test.Test",
      description: "Test connector",
      disabled: false,
      type: "observable",
      docker_based: false,
      maximum_tlp: "AMBER",
      observable_supported: ["domain", "generic", "hash", "ip", "url", "file"],
      supported_filetypes: [],
      run_hash: false,
      run_hash_type: "",
      not_supported_filetypes: [],
      params: {},
      secrets: {},
      verification: {
        configured: true,
        details: "Ready to use!",
        missing_secrets: [],
      },
      orgPluginDisabled: false,
      plugin_type: "2",
    },
  ],
  pivots: [],
  visualizers: [],
  ingestors: [],
  playbooks: [
    mockedPlaybooks.TEST_PLAYBOOK_IP,
    mockedPlaybooks.TEST_PLAYBOOK_URL,
    mockedPlaybooks.TEST_PLAYBOOK_DOMAIN,
    mockedPlaybooks.TEST_PLAYBOOK_HASH,
    mockedPlaybooks.TEST_PLAYBOOK_FILE,
    mockedPlaybooks.TEST_PLAYBOOK_GENERIC,
  ],
  hydrate: () => {},
  retrieveAnalyzersConfiguration: () => {},
  retrieveConnectorsConfiguration: () => {},
  retrieveVisualizersConfiguration: () => {},
  retrieveIngestorsConfiguration: () => {},
  retrievePlaybooksConfiguration: () => {},
  checkPluginHealth: () => {},
};
