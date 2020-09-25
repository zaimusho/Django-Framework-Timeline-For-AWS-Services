# AWS-Django-Framework-Timeline

**Django Framework on re-aligned project for differential AWS jobs timeline** <br>

**To initialise the environment, run:** <br>
**pipenv install --ignore-pipfile / pipenv run pip install -r requirements.txt** <br>
**pipenv shell** <br>
**time python awsPolling.py [-h for help on command line arguement parsing]** <br>

**AWS local creds setup** <br>
 

$ touch ~/.aws/credentials <br>
 

**Open the file and paste the structure below. Fill in the placeholders with the new user credentials you have downloaded:**
<br>
[default]<br> 

aws_access_key_id = YOUR_ACCESS_KEY_ID <br> 
 

aws_secret_access_key = YOUR_SECRET_ACCESS_KEY <br>

$ touch ~/.aws/config <br>
 
**Add the following and replace the placeholder with the region you have copied:** <br>

[default] <br>

region = YOUR_PREFERRED_REGION <br> 


**AWS DJANGO 3.0 JOBS(AWS_DJANGO):** <br>

1. pipenv install --ignore-pipfile <br>
2. pipenv shell <br>
3. python manage.py migrate (for default django databases and models route) <br>
4. python manage.py makemigrations (to update the django web framework with post written Models) <br>
5. python manage.py sqlmigrate <model_name> <migration_index for eg: 0001 from 0001_initial.py> <br>
6. python manage.py runserver 8000 <can to be changed to desired port> <br>

**OPEN THE BROWSER AND TYPE IN THE BELOW URL:** <br>

**http://locahost:8000/poller** <br>

**Tree Structure of working Django directory :** <br>

.
├── AWS_JOBS<br>
│   ├── AWS_JOBS<br>
│   │   ├── asgi.py<br>
│   │   ├── __init__.py<br>
│   │   ├── settings.py<br>
│   │   ├── urls.py<br>
│   │   └── wsgi.py<br>
│   ├── db.sqlite3<br>
│   ├── manage.py<br>
│   ├── poller<br>
│   │   ├── abstraction.py<br>
│   │   ├── admin.py<br>
│   │   ├── apps.py<br>
│   │   ├── __init__.py<br>
│   │   ├── migrations<br>
│   │   │   ├── 0001_initial.py<br>
│   │   │   └── __init__.py<br>
│   │   ├── models.py<br>
│   │   ├── static<br>
│   │   │   └── poller<br>
│   │   │       └── arn.css<br>
│   │   ├── templates<br>
│   │   │   └── poller<br>
│   │   │       ├── arnDetails.html<br>
│   │   │       ├── baseDesign.html<br>
│   │   │       ├── instanceStatus.html<br>
│   │   │       └── viewer.html<br>
│   │   ├── tests.py<br>
│   │   ├── urls.py<br>
│   │   └── views.py<br>
│   └── Pylint.txt<br>
├── Pipfile<br>
├── Pipfile.lock<br>
├── README.md<br>
└── requirements.txt<br>


**AWS Permission Policy and Trust Relationship** <br>

**Managing access to IAM roles:** <br>

Let’s dive into how you can create relationships between your enterprise identity system and your permissions system by looking at the policy types you can apply to an IAM role. <br>

**An IAM role has three places where it uses policies:** <br>

Permission policies (inline and attached) – These policies define the permissions that a principal assuming the role is able (orestricted) to perform, and on which resources. <br>
Permissions boundary – A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that aidentity-based policy can grant to an IAM entity. An entity’s permissions boundary allows it to perform only the actions that arallowed by both its identity-based permission policies and its permissions boundaries.<br>
Trust relationship – This policy defines which principals can assume the role, and under which conditions. This is sometimes referred tas a resource-based policy for the IAM role. We’ll refer to this policy simply as the ‘trust policy’.<br>

A role can be assumed by a human user or a machine principal, such as an Amazon Elastic Computer Cloud (Amazon EC2) instance or an AWS Lambda function. Over the rest of this post, you’ll see how you’re able to reduce the conditions for principals to use roles by configuring their trust policies.<br>

A common use case is when you need to provide security audit access to your account, allowing a third party to review the configuration of that account. After attaching the relevant permission policies to an IAM role, you need to add a cross-account trust policy to allow the third-party auditor to make the sts:AssumeRole API call to elevate their access in the audited account. The following trust policy shows an example policy created through the AWS Management Console:<br>


{<br>
  "Version": "2012-10-17",<br>
  "Statement": [<br>
    {<br>
      "Effect": "Allow",<br>
      "Principal": {<br>
        "AWS": "arn:aws:iam::123456789012:root"<br>
      },<br>
      "Action": "sts:AssumeRole",<br>
      "Condition": {}<br>
    }<br>
  ]<br>
}<br>

As you can see, it has the same structure as other IAM policies with Effect, Action, and Condition components. It also has the Principal parameter, but no Resource attribute. This is because the resource, in the context of the trust policy, is the IAM role itself. For the same reason, the Action parameter will only ever be set to one of the following values: sts:AssumeRole, sts:AssumeRoleWithSAML, or sts:AssumeRoleWithWebIdentity.<br>

**Note: The suffix root in the policy’s Principal attribute equates to “authenticated and authorized principals in the account,” not thspecial and all-powerful root user principal that is created when an AWS account is created.**<br>

**Using the Principal attribute to reduce scope:** <br>

In a trust policy, the Principal attribute indicates which other principals can assume the IAM role. In the example above, 123456789012 represents the AWS account number for the auditor’s AWS account. In effect, this allows any principal in the 123456789012 AWS account with sts:AssumeRole permissions to assume this role.<br>

To restrict access to a specific IAM user account, you can define the trust policy like the following example, which would allow only the IAM user LiJuan in the 123456789012 account to assume this role. LiJuan would also need to have sts:AssumeRole permissions attached to their IAM user for this to work:<br>


{<br>
  "Version": "2012-10-17",<br>
  "Statement": [<br>
    {<br>
      "Effect": "Allow",<br>
      "Principal": {<br>
        "AWS": "arn:aws:iam::123456789012:user/STSTrialRole"<br>
      },<br>
      "Action": "sts:AssumeRole",<br>
      "Condition": {}<br>
    }<br>
  ]<br>
}<br>

The principals set in the Principal attribute can be any principal defined by the IAM documentation, and can refer to an AWS or a federated principal. You cannot use a wildcard (“*” or “?”) within a Principal for a trust policy, other than one special condition, which I’ll come back to in a moment: You must define precisely which principal you are referring to because there is a translation that occurs when you submit your trust policy that ties it to each principal’s hidden principal ID, and it can’t do that if there are wildcards in the principal.<br>

The only scenario where you can use a wildcard in the Principal parameter is where the parameter value is only the “*” wildcard. Use of the global wildcard “*” for the Principal isn’t recommended unless you have clearly defined Conditional attributes in the policy statement to restrict use of the IAM role, since doing so without Conditional attributes permits assumption of the role by any principal in any AWS account, regardless of who that is.
<br>
 
