curl https://api.cloudflare.com/client/v4/\
accounts/f90ef5581b1301b7b68addfc9fa42297/r2/buckets \
	 -H 'Content-Type: application/json' \
	 -H "Authorization: Bearer $CLOUDFLARE_TOKEN" \
	 -d '{ 
				"name": "my-bucket", 
				"locationHint": "enam" 
			}'


